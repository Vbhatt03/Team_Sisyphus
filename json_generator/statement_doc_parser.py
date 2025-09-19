"""
statement_parser.py

Reusable module to parse a legal statement from a PDF.

Public API:
    parse_statement_document(file_path: str) -> dict

Core steps:
 - PDF -> high-resolution images (PyMuPDF)
 - OCR with pytesseract
 - Extract structured header fields (case info, deponent details)
 - Extract free-form narrative (statement body)
 - Clean & normalize parsed data into a hierarchical dict

Required packages:
    pip install pymupdf pytesseract pillow python-dateutil

Note:
 - On Windows you may need to set pytesseract.pytesseract.tesseract_cmd to the
   full path to your tesseract binary (example in code comments).
"""

from typing import Dict, Any, Optional, List
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import json
from datetime import datetime
import logging

# Optional flexible date parsing
try:
    from dateutil import parser as dateutil_parser  # type: ignore
except Exception:
    dateutil_parser = None

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# If needed, the user can set the tesseract path here. Example (Windows):
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def parse_statement_document(file_path: str, ocr_dpi: int = 300) -> Dict[str, Any]:
    """
    Public entry point to parse a legal statement PDF.

    Args:
        file_path: filesystem path to the PDF file.
        ocr_dpi: DPI to render each PDF page for OCR. Higher DPI can improve OCR quality.

    Returns:
        A structured dictionary containing:
            - case_info: dict (Crime No., Police Station, Dated, etc.)
            - witness_details: dict (name, father's name, age, occupation, address)
            - statement_body: dict (narrative text, start/end positions)
            - raw_text: the full OCR text
            - metadata: parsing diagnostics
    Raises:
        FileNotFoundError: if PDF cannot be opened.
        RuntimeError: OCR/render errors.
    """
    # Step 1: Extract raw OCR text from PDF
    raw_text = _extract_text_from_pdf(file_path, dpi=ocr_dpi)

    # Step 2: Parse labeled/structured header fields
    parsed_fields = _parse_structured_fields(raw_text)

    # Step 3: Extract free-form narrative body (main statement text)
    narrative_info = _extract_narrative_body(raw_text)

    # Step 4: Combine & clean parsed data
    combined = parsed_fields.copy()
    combined.update(narrative_info)
    cleaned = _clean_and_format_data(combined)

    # Compose final structured dictionary
    result = {
        "case_info": cleaned.get("case_info", {}),
        "witness_details": cleaned.get("witness_details", {}),
        "statement_body": cleaned.get("statement_body", {}),
        "raw_text": raw_text,
        "metadata": {
            "ocr_dpi": ocr_dpi,
            "fields_found": {k: bool(v) for k, v in parsed_fields.items()},
            "narrative_found": bool(narrative_info.get("narrative"))
        }
    }
    return result


def _extract_text_from_pdf(file_path: str, dpi: int = 300) -> str:
    """
    Render PDF pages to images and run OCR (pytesseract) to get text.

    Args:
        file_path: path to PDF file.
        dpi: DPI for rendering images. 300 is a good starting point.

    Returns:
        A single string with OCR text for all pages, separated by PAGE_BREAK markers.

    Raises:
        FileNotFoundError: if PDF cannot be opened.
        RuntimeError: if OCR fails.
    """
    pages_text: List[str] = []
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise FileNotFoundError(f"Unable to open PDF '{file_path}': {e}")

    try:
        for pno in range(len(doc)):
            page = doc[pno]
            mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes("png")
            try:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            except Exception as e_img:
                logger.warning("PIL failed to open page %d image: %s", pno, e_img)
                continue

            try:
                # OCR: users can add lang="eng+hin" etc. if required
                page_text = pytesseract.image_to_string(img, lang="eng")
            except Exception as e_ocr:
                raise RuntimeError(f"OCR failed on page {pno}: {e_ocr}")

            pages_text.append(page_text)
    finally:
        doc.close()

    return "\n\n---PAGE_BREAK---\n\n".join(pages_text)


def _parse_structured_fields(text_content: str) -> Dict[str, Optional[str]]:
    """
    Parse labeled structured fields from the top/headers of the statement.

    Typical fields targeted:
        - crime_no / Crime No.
        - police_station / Police Station
        - deponent_name / Name of the deponent
        - father_name / Father's name (or Husband's name variant)
        - age / Age
        - occupation / Occupation
        - residing_at / Residing at (address)
        - dated / Dated (often near signature at end)

    Approach:
        - Normalize text and split into lines.
        - Use label variant lists to locate label lines and capture the value
          either on the same line after ':' or on subsequent line(s) until
          another label or blank line appears.
    """
    # Normalize and split lines
    txt = text_content.replace("\r", "\n")
    # Collapse multiple spaces but keep newlines
    txt = re.sub(r"[ \t]+", " ", txt)
    lines = [ln.strip(" \t") for ln in txt.splitlines()]

    lower_lines = [ln.lower() for ln in lines]

    # Label variants (expand as needed)
    label_variants = {
        "crime_no": ["crime no", "crime no.", "cr. no", "crime number", "fir no", "fir no."],
        "police_station": ["police station", "ps", "police stn", "station"],
        "deponent_name": ["name of the deponent", "name of deponent", "name", "deponent"],
        "father_name": ["father's name", "father name", "son of", "daughter of", "s/o", "d/o"],
        "age": ["age", "age:"],
        "occupation": ["occupation", "profession", "employment"],
        "residing_at": ["residing at", "residing at:", "residing", "residing at address", "residing at:"],
        "dated": ["dated", "dtd", "date"]
    }

    # Prepare results dict
    extracted: Dict[str, Optional[str]] = {k: None for k in label_variants.keys()}

    # Helper to extract remainder after label on same line
    def remainder_after_label(line: str, lab: str) -> Optional[str]:
        # split by colon or dash or long dash
        parts = re.split(r'\s*[:\-–—]\s*', line, maxsplit=1)
        if len(parts) >= 2:
            return parts[1].strip()
        # if label directly followed by value separated by whitespace
        after = re.sub(re.escape(lab), "", line, flags=re.IGNORECASE).strip(" :\-–—")
        return after if after else None

    # Known label regex for stopping block capture
    all_labels_lower = [re.escape(lab.lower()) for variants in label_variants.values() for lab in variants]
    known_label_re = re.compile("|".join(sorted(all_labels_lower, key=len, reverse=True))) if all_labels_lower else None

    # First pass: locate each label in lines and capture same-line or following lines until another label/blank
    for idx, ln in enumerate(lower_lines):
        for key, variants in label_variants.items():
            if extracted[key]:
                continue  # already found
            for lab in variants:
                if lab in ln:
                    # Attempt same-line value
                    orig_line = lines[idx]
                    val = remainder_after_label(orig_line, lab)
                    if val:
                        extracted[key] = val.strip(" ,.;:")
                        break
                    # Otherwise capture next consecutive non-empty lines until blank or new label
                    j = idx + 1
                    captured = []
                    while j < len(lines):
                        candidate = lines[j].strip()
                        if not candidate:
                            break
                        if known_label_re and known_label_re.search(candidate.lower()):
                            break
                        captured.append(candidate)
                        j += 1
                    if captured:
                        extracted[key] = " ".join(captured).strip(" ,.;:")
                    break
            if extracted[key]:
                break

    # Heuristic fallback for deponent name: look for "I, <Name>" at top of the doc
    if not extracted.get("deponent_name"):
        # look in the first 12 lines for pattern "I, <name> ..." or "<name> (age ...)"
        head = "\n".join(lines[:12])
        m = re.search(r'\bI[, ]+\s*([A-Z][A-Za-z\.\- ]{2,80}?)\b(?:\s|,|\()', head)
        if m:
            extracted["deponent_name"] = m.group(1).strip(" ,.")

    # For father's name / s/o d/o pattern
    if not extracted.get("father_name"):
        m = re.search(r'\b(?:s\/o|s\.?o\.?|son of|daughter of|d\/o|d\.?o\.?)\s+([A-Z][A-Za-z\. \-]{2,80})', text_content, re.IGNORECASE)
        if m:
            extracted["father_name"] = m.group(1).strip(" ,.")

    # For age if not found: look for e.g., 'aged 32', 'age: 32 years'
    if not extracted.get("age"):
        m = re.search(r'\b(age|aged)\s*[:\-]?\s*(\d{1,3})', text_content, re.IGNORECASE)
        if m:
            extracted["age"] = m.group(2)

    # Normalize empty strings to None
    for k, v in list(extracted.items()):
        if isinstance(v, str):
            v2 = v.strip()
            extracted[k] = v2 if v2 else None
        else:
            extracted[k] = None

    return extracted


def _extract_narrative_body(text_content: str) -> Dict[str, Optional[str]]:
    """
    Extracts the free-form narrative portion of the statement.

    Strategy:
      - Look for common start phrases like:
          "I do hereby on solemn affirmation state", "I do hereby solemnly affirm and say",
          "I, <name>, do hereby state", "The deponent states as follows", "I state as follows"
      - Once a start is found, find an end via common ending phrases or signature blocks:
          "I do not wish to say anything more.", "I say nothing more.", "That's all I have to say.",
          "Signature", "Deponent", "Signed", "Date:", "Dated:"
      - If start is not found, fall back to heuristics: capture the large middle block
        after header fields and before signature block.
    Returns:
        dict with keys:
          - narrative: extracted narrative text (or None)
          - narrative_start_index: approximate start position (character index) in raw text (or None)
          - narrative_end_index: approximate end position (or None)
    """
    txt = text_content
    lower = txt.lower()

    # Common start patterns (try them in order)
    start_phrases = [
        r'i do hereby on solemn affirmation state', 
        r'i do hereby solemnly affirm and say',
        r'i do hereby state', 
        r'the deponent states as follows',
        r'i state as follows', 
        r'statement', 
        r'deponent states'
    ]
    # Common end patterns
    end_phrases = [
        r'i do not wish to say anything more', 
        r'i say nothing more', 
        r'that is all i have to say', 
        r"that's all i have to say", 
        r'signature', r'signed', r'deponent', r'witness', r'dated[:\s]', r'date[:\s]'
    ]

    # Find earliest occurrence of any start phrase
    start_pos = None
    start_match_text = None
    for sp in start_phrases:
        m = re.search(sp, lower, re.IGNORECASE)
        if m:
            start_pos = m.start()
            start_match_text = txt[m.start():m.end()]
            break

    # If start phrase found: search for an end phrase after it
    if start_pos is not None:
        # consider substring from start to end of doc
        tail = txt[start_pos:]
        end_pos = None
        for ep in end_phrases:
            m2 = re.search(ep, tail, re.IGNORECASE)
            if m2:
                end_pos = start_pos + m2.start()
                break
        if end_pos is None:
            # as fallback, look for last occurrence of typical 'Signature' or 'Deponent' near end
            m_sig = re.search(r'(signature|signed|deponent|witness)', tail[::-1], re.IGNORECASE)
            if m_sig:
                # reverse-search fallback is tricky; we'll instead search from the end
                for ep in end_phrases:
                    m3 = re.search(ep, txt[start_pos:], re.IGNORECASE)
                    if m3:
                        end_pos = start_pos + m3.start()
                        break
        if end_pos is None:
            # as last resort, take up to 1500 characters or end of doc
            end_pos = min(len(txt), start_pos + 5000)

        narrative = txt[start_pos:end_pos].strip()
        return {
            "narrative": narrative if narrative else None,
            "narrative_start_index": start_pos,
            "narrative_end_index": end_pos
        }

    # If start phrase not found: heuristic approach
    # Try to find the "signature block" near the end, usually contains words like 'Deponent', 'Signature', 'Dated'
    sig_re = re.search(r'(?:\n|\r)(?:\s*)(signature|signed|deponent|witness|dtd|dated)[:\s]?.{0,120}$', txt, re.IGNORECASE | re.MULTILINE)
    if sig_re:
        sig_pos = sig_re.start()
        # capture large chunk before signature block as potential narrative
        # but avoid capturing header info; attempt to start after first blank line following header lines
        # heuristically skip first 2000 characters if doc is huge
        head_cut = 200  # skip first ~200 characters that are header-like
        narrative = txt[head_cut:sig_pos].strip()
        # further refine by removing top header lines if they contain many labels (e.g., 'Crime No.')
        # Look for first occurrence of "I " or "The deponent" within the candidate and start there
        mstart = re.search(r'\bI\s+(do|hereby|state|depose|,)|the deponent', narrative, re.IGNORECASE)
        if mstart:
            ns = mstart.start()
            narrative = narrative[ns:].strip()
            return {
                "narrative": narrative if narrative else None,
                "narrative_start_index": head_cut + ns,
                "narrative_end_index": sig_pos
            }
        return {
            "narrative": narrative if narrative else None,
            "narrative_start_index": head_cut,
            "narrative_end_index": sig_pos
        }

    # As a last resort: return the whole document as narrative (poor quality fallback)
    short = txt.strip()
    return {
        "narrative": short if short else None,
        "narrative_start_index": 0 if short else None,
        "narrative_end_index": len(short) if short else None
    }


def _clean_and_format_data(parsed_data: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Convert the raw parsed strings to structured, typed data and assemble hierarchical groups.

    Input: parsed_data can include keys from _parse_structured_fields + _extract_narrative_body:
        - crime_no, police_station, deponent_name, father_name, age, occupation, residing_at, dated
        - narrative, narrative_start_index, narrative_end_index

    Output:
        {
            "case_info": {...},
            "witness_details": {...},
            "statement_body": {...}
        }
    """
    def _strip(v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) and v.strip() else None

    def _parse_age(a: Optional[str]) -> Optional[int]:
        if not a: return None
        m = re.search(r'(\d{1,3})', a)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return None
        return None

    def _parse_date(s: Optional[str]) -> Optional[str]:
        if not s: return None
        s0 = s.strip()
        # try dateutil if available
        if dateutil_parser:
            try:
                dt = dateutil_parser.parse(s0, fuzzy=True, dayfirst=False)
                return dt.isoformat()
            except Exception:
                pass
        # try common formats
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%B %d, %Y", "%Y-%m-%d"]
        for fmt in formats:
            try:
                dt = datetime.strptime(s0, fmt)
                return dt.isoformat()
            except Exception:
                pass
        # fallback: extract date-like substring
        m = re.search(r'(\d{1,2}[\/\-\s]\d{1,2}[\/\-\s]\d{2,4}|\w+\s+\d{1,2},\s*\d{4})', s0)
        if m:
            try:
                if dateutil_parser:
                    dt = dateutil_parser.parse(m.group(0), fuzzy=True)
                    return dt.isoformat()
            except Exception:
                pass
        return None

    # Assemble witness_details
    witness_details = {
        "name": _strip(parsed_data.get("deponent_name")),
        "father_name": _strip(parsed_data.get("father_name")),
        "age": _parse_age(parsed_data.get("age")),
        "occupation": _strip(parsed_data.get("occupation")),
        "residing_at": _strip(parsed_data.get("residing_at"))
    }

    # Assemble case_info
    case_info = {
        "crime_no": _strip(parsed_data.get("crime_no")),
        "police_station": _strip(parsed_data.get("police_station")),
        "dated_raw": _strip(parsed_data.get("dated")),
        "dated_iso": _parse_date(parsed_data.get("dated"))
    }

    # Narrative / statement body
    statement_body = {
        "narrative": _strip(parsed_data.get("narrative")),
        "narrative_start_index": parsed_data.get("narrative_start_index"),
        "narrative_end_index": parsed_data.get("narrative_end_index")
    }

    return {
        "witness_details": witness_details,
        "case_info": case_info,
        "statement_body": statement_body
    }
