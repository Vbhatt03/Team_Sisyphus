# statement_doc_parser.py
import json
import re
import requests
import fitz
import os
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This OCR function remains unchanged as it is already modular
def extract_text_with_ocrspace_api(pdf_path: str, api_key: str) -> str:
    if not os.path.exists(pdf_path):
        logging.error(f"File not found at path: {pdf_path}")
        return ""
    full_text: List[str] = []
    ocr_url = 'https://api.ocr.space/parse/image'
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        for start in range(0, total_pages, 3):
            end = min(start + 3, total_pages)
            logging.info(f"Processing pages {start + 1} to {end} of {total_pages}...")
            batch_images = []
            for page_num in range(start, end):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                batch_images.append(img_bytes)
            for i, img_bytes in enumerate(batch_images):
                files = {'file': (f'page_{start+i+1}.png', img_bytes, 'image/png')}
                payload = {'isOverlayRequired': False, 'apikey': api_key, 'language': 'eng'}
                response = requests.post(ocr_url, files=files, data=payload)
                response.raise_for_status()
                result = response.json()
                if result.get('IsErroredOnProcessing'):
                    logging.error(f"OCR.space API error on page {start+i+1}: {result.get('ErrorMessage')}")
                    continue
                parsed_text = result['ParsedResults'][0]['ParsedText']
                full_text.append(parsed_text)
        doc.close()
    except Exception as e:
        logging.error(f"An error occurred during PDF processing or API call: {e}")
        return ""
    return "\n".join(full_text)

# --- Updated core parsing logic for the new PDF format ---
def parse_statement_data(text: str) -> dict:
    """Parses extracted text from the statement.pdf format and redacts sensitive info."""
    data = {}
    def clean_value(value: str | None) -> str | None:
        return value.strip().strip(':., ') if value else None

    # Use a more generic regex to find any police station name
    crime_no = re.search(r"Crime No\s*\.?\s*([\d\/]+)", text, re.IGNORECASE)
    police_station = re.search(r"(\w+\s+Police\s+Station)", text, re.IGNORECASE)
    court = re.search(r"IN THE COURT OF THE (.*?)\n", text, re.IGNORECASE)
    under_sections = re.search(r"U/s (.*?)\n", text, re.IGNORECASE)

    data['case_info'] = {
        "crime_no": clean_value(crime_no.group(1)) if crime_no else None,
        "police_station": clean_value(police_station.group(1)) if police_station else None,
        "court": clean_value(court.group(1)) if court else None,
        "under_sections": clean_value(under_sections.group(1)) if under_sections else None
    }

    # Occupation is captured, other personal details are redacted by design
    occupation = re.search(r"Occupation\s*:\s*(.*?)\n", text, re.IGNORECASE)
    data['witness_details'] = {
        "name": None, "father_name": None, "age": None,
        "occupation": clean_value(occupation.group(1)) if occupation else None,
        "address": None
    }

    # More flexible regex for statement type and date
    statement_type = re.search(r"Statement under section\s*(.*?)\n", text, re.IGNORECASE)
    statement_date = re.search(r"Date(?:d)?\s*:\s*([\d\.\/]+)", text, re.IGNORECASE)
    data['statement_details'] = {
        "type": clean_value(f"Statement under section {statement_type.group(1)}") if statement_type else None,
        "date": clean_value(statement_date.group(1)) if statement_date else None
    }
    
    # Narrative extraction with updated cleaning logic
    narrative_start_marker = r"I (?:say|do hereby)"
    narrative_end_marker = r"I do not wish to say anything more"
    narrative_block_match = re.search(f"({narrative_start_marker}.*?){narrative_end_marker}", text, re.DOTALL | re.IGNORECASE)
    
    if narrative_block_match:
        narrative_raw = narrative_block_match.group(1)
        lines = narrative_raw.strip().split('\n')
        # Updated regex to remove artifacts specific to the new PDF format
        cleaned_lines = [
            line.strip() for line in lines 
            if not re.match(r"^\s*(Crime No|Panaji Police Station|Priya|Page \d+)\s*$", line.strip(), re.IGNORECASE)
        ]
        data['narrative'] = " ".join(cleaned_lines)
    else:
        data['narrative'] = None
        
    return data
# --- End of core logic ---

# This orchestration function remains unchanged
def process_statement_pdf(pdf_path: str, api_key: str) -> dict:
    """Orchestrates the extraction and parsing for a single statement PDF."""
    logging.info(f"Processing Statement: {os.path.basename(pdf_path)}")
    statement_text = extract_text_with_ocrspace_api(pdf_path, api_key)
    if not statement_text:
        return {"error": "Text extraction failed."}
    
    parsed_data = parse_statement_data(statement_text) # Calls the updated parsing function
    return parsed_data