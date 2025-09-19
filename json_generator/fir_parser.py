"""
fir_parser.py

Robust FIR PDF -> structured dictionary parser.

This module:
 - Renders PDF pages with PyMuPDF (fitz) to images, OCRs them with pytesseract,
 - Extracts labeled fields using flexible label matching (works across form variations),
 - Cleans and normalizes parsed values (dates -> ISO, numeric parsing, address normalization).

This version was tuned with two example FIR files the user provided (for regex/label
selection heuristics): FIR.pdf and FORM IF 1 (fir).pdf. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

Required packages:
    pip install pymupdf pytesseract pillow python-dateutil

If using on Windows, set pytesseract.pytesseract.tesseract_cmd to your Tesseract binary, e.g.
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
"""

from typing import Dict, Any, Optional, List, Tuple
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from datetime import datetime
import logging

# Optional: flexible date parsing
try:
    from dateutil import parser as dateutil_parser  # type: ignore
except Exception:
    dateutil_parser = None

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_fir_document(file_path: str, ocr_dpi: int = 300) -> Dict[str, Any]:
    """
    Primary entry point for parsing an FIR PDF file.

    Args:
        file_path: Path to the FIR PDF to parse.
        ocr_dpi: DPI to render PDFs for OCR (higher can improve OCR accuracy).

    Returns:
        A dictionary with cleaned and structured FIR fields.

    Raises:
        FileNotFoundError: If the PDF cannot be opened.
        RuntimeError: If OCR/pdf rendering fails.
    """
    text = _extract_text_from_pdf(file_path, dpi=ocr_dpi)
    raw = _parse_structured_fields(text)
    cleaned = _clean_and_format_data(raw)
    return cleaned


def _extract_text_from_pdf(file_path: str, dpi: int = 300) -> str:
    """
    Convert PDF pages to images and use pytesseract to extract text.

    Args:
        file_path: Path to PDF file.
        dpi: DPI for rendering; higher -> larger images -> better OCR.

    Returns:
        Concatenated OCR text for all pages (with PAGE_BREAK markers between pages).

    Raises:
        FileNotFoundError: If file can't be opened.
        RuntimeError: If OCR fails on a page.
    """
    pages_text: List[str] = []
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise FileNotFoundError(f"Cannot open PDF '{file_path}': {e}")

    try:
        for i in range(len(doc)):
            page = doc[i]
            # Render page to image bytes
            mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))

            # OCR (English). Users can add lang parameter if needed.
            try:
                page_text = pytesseract.image_to_string(img, lang="eng")
            except Exception as e_ocr:
                raise RuntimeError(f"OCR failed on page {i}: {e_ocr}")

            pages_text.append(page_text)
    finally:
        doc.close()

    # Join pages to produce a single text blob; keep page-break markers
    return "\n\n---PAGE_BREAK---\n\n".join(pages_text)


def _parse_structured_fields(text_content: str,
                             label_variants: Optional[Dict[str, List[str]]] = None
                             ) -> Dict[str, Optional[str]]:
    """
    Extract labeled fields from OCR text.

    Approach:
      1. Normalize text and split into lines.
      2. Attempt line-based key:value extraction (common for forms).
      3. Use block extraction for multi-line fields (Narration/Statement/Address).
      4. Use configured label variants to be robust across forms.

    Args:
        text_content: Raw OCR text.
        label_variants: Optional mapping of canonical keys to list of label strings
                        to match in OCR text. If None, default variants will be used.

    Returns:
        Dict mapping canonical keys to raw extracted string (or None).
    """
    # Default label variants (tuned for common FIR forms)
    default_variants = {
        "fir_no": ["F.I.R. No", "FIR No", "FIR No.", "FIR", "F.I.R", "FIR Number", "F.I.R. Number"],
        "date": ["Date", "Dated", "Date of Occurrence", "Date:"],
        "time": ["Time", "Time of Occurrence", "At"],
        "complainant_name": ["Name of Complainant", "Complainant", "Name (Complainant)", "Name"],
        "victim_name": ["Name of Victim", "Victim"],
        "accused_name": ["Name of Accused", "Accused"],
        "place_of_occurrence": ["Place of Occurrence", "Place", "Location", "Occurence", "Occurence at"],
        "occurrence_datetime": ["Date & Time of Occurrence", "Date and Time of Occurrence", "Date & Time"],
        "sections": ["Sections", "Sections under", "Section(s)"],
        "address": ["Address", "Address of Complainant", "Address of Victim"],
        "narration": ["Narration", "Brief Facts", "Statement of Facts", "Information", "Factual Narrative", "Brief Facts/Statement"],
        "total_value": ["Total value", "Value of property", "Estimated value", "Value"]
    }

    variants = label_variants if label_variants is not None else default_variants

    # Normalize OCR text
    txt = text_content.replace("\r", "\n")
    txt = re.sub(r"\n\s+\n", "\n\n", txt)  # collapse lines with spaces
    txt = re.sub(r"[ \t]+", " ", txt)

    # Split into lines and keep indexes for block extraction
    lines = [ln.strip(" \t") for ln in txt.splitlines()]

    # Prepare result dict
    results: Dict[str, Optional[str]] = {k: None for k in variants.keys()}

    # Build a case-insensitive map of line -> index for searching
    lower_lines = [ln.lower() for ln in lines]

    # Helper: try to extract value after a label on the same line
    def _extract_from_line(label: str, line: str) -> Optional[str]:
        # possible separators
        sep_match = re.split(r'\s*[:\-–—]\s*', line, maxsplit=1)
        if len(sep_match) >= 2:
            return sep_match[1].strip()
        # if no separator, try label removal
        after = re.sub(re.escape(label), "", line, flags=re.IGNORECASE).strip(" :\-–—")
        return after if after else None

    # First pass: line-by-line label:value extraction
    for idx, ln in enumerate(lines):
        low = ln.lower()
        for key, labels in variants.items():
            if results.get(key):  # already found
                continue
            for lab in labels:
                lab_low = lab.lower()
                # If line contains label text
                if lab_low in low:
                    # Extract value on same line, if present
                    val = _extract_from_line(lab, ln)
                    if val:
                        results[key] = val
                        break
            if results.get(key):
                break

    # Second pass: block extraction for fields that are typically multiline (narration, address)
    # locate label line index, then capture subsequent lines until a blank or another known-label line
    label_keys_for_blocks = ["narration", "address"]
    known_label_patterns = []
    for labels in variants.values():
        for lab in labels:
            # build safe regex fragment
            known_label_patterns.append(re.escape(lab.lower()))
    known_labels_re = re.compile("|".join(sorted(known_label_patterns, key=len, reverse=True))) if known_label_patterns else None

    for blk_key in label_keys_for_blocks:
        if results.get(blk_key):
            continue  # already found in first pass
        labels = variants.get(blk_key, [])
        # find a line that contains any of these labels
        for idx, ln in enumerate(lower_lines):
            if any(lab.lower() in ln for lab in labels):
                # Capture following lines (including the current line's remainder)
                # Start with remainder of current line after label
                original_line = lines[idx]
                # Attempt to get text on same line after separator
                remainder = _extract_from_line(labels[0], original_line) or ""
                captured_lines = [remainder] if remainder else []
                # capture subsequent non-empty lines until we hit a line that looks like a new label or a blank line
                j = idx + 1
                while j < len(lines):
                    candidate = lines[j].strip()
                    if not candidate:
                        # blank line -> likely end of block
                        break
                    # if the candidate line contains other known labels, stop
                    if known_labels_re and known_labels_re.search(candidate.lower()):
                        break
                    captured_lines.append(candidate)
                    j += 1
                joined = "\n".join([c for c in captured_lines if c]).strip()
                if joined:
                    results[blk_key] = joined
                break

    # Third pass: fallback heuristics (scan for common label tokens anywhere)
    # If still missing common fields, try looser regex search for label followed by value on same or next line
    for key, labels in variants.items():
        if results.get(key):
            continue
        for lab in labels:
            # regex: label ... (up to newline or up to 200 chars)
            pattern = re.compile(re.escape(lab) + r'\s*[:\-–—]?\s*(?P<v>.{1,300}?)\n', re.IGNORECASE | re.DOTALL)
            m = pattern.search(txt)
            if m:
                val = m.group("v").strip(" \n\r\t-.:;")
                if val:
                    results[key] = val
                    break
        if results.get(key):
            continue

    # Simple cleanup: None/empty -> None
    for k, v in list(results.items()):
        if isinstance(v, str):
            v2 = v.strip()
            results[k] = v2 if v2 else None
        else:
            results[k] = None

    return results


def _clean_and_format_data(parsed_data: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Clean and normalize parsed fields:
      - Convert date strings to ISO-format where possible.
      - Parse numeric values (total_value) to float.
      - Normalize FIR No, Names, Address, and split Sections into list.

    Args:
        parsed_data: Raw dictionary (strings or None).

    Returns:
        Dictionary with cleaned fields and added convenience keys (e.g., date_iso).
    """
    def _strip(s: Optional[str]) -> Optional[str]:
        return s.strip() if s and isinstance(s, str) else None

    def _parse_date(s: Optional[str]) -> Optional[str]:
        if not s:
            return None
        s0 = s.strip()
        # Try dateutil first for flexible parsing
        if dateutil_parser:
            try:
                dt = dateutil_parser.parse(s0, fuzzy=True, dayfirst=False)
                return dt.isoformat()
            except Exception:
                pass
        # Try common explicit formats
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%d %B, %Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(s0, fmt)
                return dt.isoformat()
            except Exception:
                continue
        # Attempt to find a date-like substring
        m = re.search(r'(\d{1,2}[\/\-\s]\d{1,2}[\/\-\s]\d{2,4}|\w+\s+\d{1,2},\s*\d{4})', s0)
        if m:
            try:
                if dateutil_parser:
                    dt = dateutil_parser.parse(m.group(0), fuzzy=True)
                    return dt.isoformat()
            except Exception:
                pass
        return None

    def _parse_number(s: Optional[str]) -> Optional[float]:
        if not s:
            return None
        # Remove non-numeric chars except . and ,
        t = re.sub(r'[^\d\.,\-]', '', s)
        # Heuristics: if both . and , present, remove commas
        try:
            if t.count('.') > 0 and t.count(',') > 0:
                t2 = t.replace(',', '')
            else:
                # If only commas and looks like decimal comma (e.g., 123,45) -> swap to dot
                if t.count(',') == 1 and re.search(r',\d{1,2}$', t):
                    t2 = t.replace(',', '.')
                else:
                    t2 = t.replace(',', '')
            return float(t2)
        except Exception:
            digits = re.findall(r'\d+', t)
            if digits:
                try:
                    return float("".join(digits))
                except Exception:
                    return None
            return None

    out: Dict[str, Any] = {}

    # Copy & strip textual fields
    for key, val in parsed_data.items():
        out[key] = _strip(val)

    # Date fields
    if out.get("date"):
        out["date_iso"] = _parse_date(out["date"])
    if out.get("occurrence_datetime"):
        # Try to parse entire datetime or extract date/time parts
        dt_iso = _parse_date(out["occurrence_datetime"])
        out["occurrence_datetime_iso"] = dt_iso
        # If no separate date exists, and we extracted occurrence datetime, populate date_iso
        if not out.get("date") and dt_iso:
            out["date_iso"] = dt_iso

    if out.get("time"):
        out["time_clean"] = _strip(out["time"])

    # FIR number normalization
    if out.get("fir_no"):
        # Remove extraneous characters, keep alphanumerics, hyphen, slash
        out["fir_no_normalized"] = re.sub(r'[^A-Za-z0-9\/\-]', '', out["fir_no"])

    # Names
    for name_key in ("complainant_name", "victim_name", "accused_name"):
        if out.get(name_key):
            # Remove excessive whitespace and trailing tokens
            s = re.sub(r'\s{2,}', ' ', out[name_key]).strip(" ,.")
            out[name_key] = s

    # Address normalization: collapse newlines to commas
    if out.get("address"):
        addr = re.sub(r'\n+', ', ', out["address"])
        addr = re.sub(r'\s{2,}', ' ', addr)
        out["address_normalized"] = addr.strip(" ,")

    # Sections -> list
    if out.get("sections"):
        # Split by commas, slashes, semicolon, or whitespace + slash
        parts = re.split(r'[,\n;/]+|\s+/\s+', out["sections"])
        parts = [p.strip() for p in parts if p and p.strip()]
        # Further split tokens like "IPC 379/34" into "IPC 379", "34" only if desired — keeping as-is for now
        out["sections_list"] = parts if parts else None

    # Total value numeric
    if out.get("total_value"):
        out["total_value_numeric"] = _parse_number(out["total_value"])

    # Narration cleanup
    if out.get("narration"):
        narration = re.sub(r'\n{2,}', '\n', out["narration"]).strip()
        out["narration_clean"] = narration

    return out
