import os
import json
import requests
import re
import fitz  # PyMuPDF
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_ocr_space_on_pages(pdf_path, start_page, end_page, api_key):
    """Passes API key instead of using a global one."""
    text_blocks = []
    doc = fitz.open(pdf_path)
    end_page = min(end_page, len(doc))
    
    for page_num in range(start_page, end_page):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        
        resp = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("page.png", img_bytes, "image/png")},
            data={"apikey": api_key, "OCREngine": 2, "language": "eng"},
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("IsErroredOnProcessing"):
            raise Exception(f"OCR.space error: {result.get('ErrorMessage')}")
        
        text_blocks.append(result["ParsedResults"][0].get("ParsedText", ""))
    
    doc.close()
    return "\n\n".join(text_blocks)

def extract_text_from_pdf_in_batches(pdf_path, api_key):
    """Passes API key down to the OCR function."""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    full_text = []
    MAX_PAGES_PER_BATCH = 3
    for start in range(0, total_pages, MAX_PAGES_PER_BATCH):
        end = start + MAX_PAGES_PER_BATCH
        batch_text = run_ocr_space_on_pages(pdf_path, start, end, api_key)
        full_text.append(batch_text)
    
    return "\n\n".join(full_text)

# --- Core parsing logic (Modified for Security) ---
def parse_fir_data(text):
    """
    Parses FIR text into structured JSON, with sensitive PII fields
    hardcoded to null for security.
    """
    data = {}

    # 1️⃣ FIR basic details (Non-sensitive - Parsed as normal)
    fir_match = re.search(
        r"P\.S\.\s*(.*?)\s*[\r\n]+Year\s*(\d{4})\s*[\r\n]+FIR\s*No\.?\s*([\d\/]+)\s*[\r\n]+Date\s*[:\-]?\s*([\d\/\-]+)",
        text, re.IGNORECASE
    )
    if fir_match:
        data['police_station'] = fir_match.group(1).strip()
        data['year'] = fir_match.group(2).strip()
        data['fir_no'] = fir_match.group(3).strip()
        data['fir_date'] = fir_match.group(4).strip()
    else:
        # Fallback for non-sensitive data
        ps_match = re.search(r"(\b[A-Z][a-zA-Z\s]+)\s+PS", text)
        fir_no_match = re.search(r"Cr\.?\s*No\.?\s*([\d\/]+)", text, re.IGNORECASE)
        data['police_station'] = ps_match.group(1).strip() if ps_match else None
        data['fir_no'] = fir_no_match.group(1).strip() if fir_no_match else None
        data.update({'year': None, 'fir_date': None})

    # 2️⃣ Acts and Sections (Non-sensitive - Parsed as normal)
    acts_and_sections = []
    bns_match = re.search(r"BHARATIYA\s+NYAYA\s+SANHITA.*?(\d+\(\d+\))", text, re.IGNORECASE | re.DOTALL)
    if bns_match:
        acts_and_sections.append({
            "act": "THE BHARATIYA NYAYA SANHITA (BNS), 2023",
            "section": bns_match.group(1)
        })
    goa_act_match = re.search(r"Goa\s+Children.?s\s+Act\s+2003\s*([\d]+)", text, re.IGNORECASE)
    if goa_act_match:
        acts_and_sections.append({
            "act": "The Goa Children's Act 2003",
            "section": goa_act_match.group(1).strip()
        })
    data['acts_and_sections'] = acts_and_sections

    # 3️⃣ Complainant/Informant (MODIFIED FOR SECURITY)
    # This entire block is now hardcoded to null to protect personal information.
    data['complainant_informant'] = {
        "name": None,
        "address": None
    }

    # 4️⃣ Accused Details (MODIFIED FOR SECURITY)
    # This is hardcoded to null to protect personal information.
    data['accused_details'] = [{
        "name": None,
        "address": None
    }]

    # 5️⃣ Brief Facts (MODIFIED FOR SECURITY)
    # The narrative is redacted entirely by setting it to null, as it can contain sensitive details.
    data['brief_facts'] = None

    return data
# --- End of core logic ---

def process_fir_pdf(pdf_path: str, api_key: str) -> dict:
    """Orchestrates the extraction and parsing for a single FIR PDF."""
    logging.info(f"Processing FIR: {os.path.basename(pdf_path)}")
    text = extract_text_from_pdf_in_batches(pdf_path, api_key)
    if not text.strip():
        return {"error": "Text extraction failed."}

    parsed_data = parse_fir_data(text) # Calls the security-modified function
    parsed_data['source_pdf'] = os.path.basename(pdf_path)
    return parsed_data