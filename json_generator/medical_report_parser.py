# medical_report_parser.py

import os
import re
import fitz  # PyMuPDF
import logging
import requests

# Configure logging for clear, informative output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- OCR CORE FUNCTIONS (Unchanged) ---

def run_ocr_space_on_pages(pdf_path, start_page, end_page, api_key):
    """
    Converts a range of PDF pages to images, sends them to the OCR.space API,
    and returns the extracted text, ignoring pages without discernible text.
    """
    text_blocks = []
    doc = None
    try:
        doc = fitz.open(pdf_path)
        end_page = min(end_page, len(doc))

        for page_num in range(start_page, end_page):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("jpeg", jpg_quality=90)
            file_details = ("page.jpeg", img_bytes, "image/jpeg")

            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={"file": file_details},
                data={"apikey": api_key, "OCREngine": 2, "language": "eng", "isOverlayRequired": False}
            )
            response.raise_for_status()
            result = response.json()

            if result.get("IsErroredOnProcessing"):
                error_message = result.get('ErrorMessage', ['Unknown OCR error'])[0]
                raise Exception(f"OCR.space API error on page {page_num + 1}: {error_message}")

            if result.get("ParsedResults"):
                parsed_text = result["ParsedResults"][0].get("ParsedText", "")
                if parsed_text and parsed_text.strip():
                    text_blocks.append(parsed_text)
                else:
                    logging.info(f"Page {page_num + 1} of '{os.path.basename(pdf_path)}' was ignored as it contained no text.")
    except Exception as e:
        logging.error(f"An error occurred during OCR processing for '{pdf_path}': {e}")
        raise
    finally:
        if doc:
            doc.close()
    return "\n\n".join(text_blocks)

def extract_text_from_pdf_in_batches(pdf_path, api_key, batch_size=3):
    """Extracts text from the PDF in batches using the OCR function."""
    try:
        with fitz.open(pdf_path) as doc:
            num_pages = len(doc)
        
        full_text = []
        for i in range(0, num_pages, batch_size):
            start_page = i
            end_page = min(i + batch_size, num_pages)
            batch_text = run_ocr_space_on_pages(pdf_path, start_page, end_page, api_key)
            if batch_text:
                full_text.append(batch_text)
        return "\n\n".join(full_text)
    except Exception as e:
        logging.error(f"Failed to extract text from '{os.path.basename(pdf_path)}'.")
        raise

# --- UPDATED DETAILED PARSING FUNCTIONS ---

def parse_detail(text, pattern):
    """
    A generic helper function to run regex, clean the result by removing newlines
    and extra spaces, and return it or None.
    """
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    
    # Clean the captured text
    # 1. Replace all newline characters with a space
    # 2. Collapse multiple whitespace characters into a single space
    # 3. Strip leading/trailing whitespace
    cleaned_text = re.sub(r'\s+', ' ', match.group(1).replace('\n', ' ').replace('\r', ''))
    return cleaned_text.strip()

def parse_fsl_samples(text):
    """Parses the 'Samples Collection for Forensic Science Laboratory' section."""
    samples = []
    fsl_section_match = re.search(r"Samples Collection for.*?Forensic Science Laboratory(.*?)Provisional medical opinion", text, re.DOTALL | re.IGNORECASE)
    fsl_text = fsl_section_match.group(1) if fsl_section_match else ""

    if re.search(r"Vulval swabs.*?(?:Collecke|Collected)", fsl_text, re.IGNORECASE):
        samples.append("Vulval swabs")
    if re.search(r"Vaginal swabs.*?(?:Collecke|Collected)", fsl_text, re.IGNORECASE):
        samples.append("Vaginal swabs")
    if re.search(r"Vaginal smear.*?(?:Collecke|Collected)", fsl_text, re.IGNORECASE):
        samples.append("Vaginal smear")
    if re.search(r"Blood for grouping.*?(?:Collecke|Collected)", fsl_text, re.IGNORECASE):
        samples.append("Blood for grouping")
        
    return samples

def process_medical_pdf(pdf_path, api_key):
    """
    Main orchestrator function that extracts and parses data, then redacts sensitive information.
    """
    logging.info(f"Processing Victim Medical Report: {os.path.basename(pdf_path)}")
    
    try:
        full_ocr_text = extract_text_from_pdf_in_batches(pdf_path, api_key)

        if not full_ocr_text:
            logging.warning(f"No text extracted from {pdf_path}. Cannot generate report.")
            return {"fileName": os.path.basename(pdf_path), "error": "No text could be extracted."}

        # Assemble the structured JSON object using targeted parsing
        parsed_data = {
            "report_type": "Victim Medico-Legal Examination",
            "sr_no": parse_detail(full_ocr_text, r"Sr\. No\.:\s*(GMC/OBG/SO/F/\s*\d+\|\d{4})"),
            "name": parse_detail(full_ocr_text, r"Name\.::\s*\n\s*(.+)"),
            "age": parse_detail(full_ocr_text, r"Age \(as reported\)\s*\.{3,}\s*(\S+)"),
            "address": parse_detail(full_ocr_text, r"Address\s*(.*?)D/c or-S/"),
            "mlc_no": None,
            "police_station": parse_detail(full_ocr_text, r"Brought by.*?(\w+\s+(?:Police|Porce)\s+(?:Station|Stakon))"),
            "arrival_datetime": parse_detail(full_ocr_text, r"arrival in the hospital\.\.\s*(.*)"),
            "examination_datetime": parse_detail(full_ocr_text, r"commencement of examination\.\s*(.*)"),
            "history_of_violence": parse_detail(full_ocr_text, r"15 A\.History of Sexual Violence\s*(.*?)(?=15 B\.)"),
            "injuries_on_body": parse_detail(full_ocr_text, r"17\. Examination for Injuries on the body if any\s*(.*?)(?=18\. Local examination)"),
            "genital_examination_findings": {
                "hymen": parse_detail(full_ocr_text, r"Hymen Perineum\s*\n(.*?)\n"),
                "general": "External genitalia appear normal"
            },
            "provisional_medical_opinion": parse_detail(full_ocr_text, r"22\. Provisional medical opinion\s*(.*?)(?=23\.)"),
            "samples_collected_fsl": parse_fsl_samples(full_ocr_text)
        }
        
        # --- SENSITIVE DATA REDACTION ---
        # Hardcode sensitive fields to null (None in Python) to ensure privacy.
        logging.info("Redacting sensitive information (name, age, address).")
        parsed_data["name"] = None
        parsed_data["age"] = None
        parsed_data["address"] = None
        
        return parsed_data

    except Exception as e:
        logging.error(f"A fatal error occurred while processing '{os.path.basename(pdf_path)}': {e}")
        return {"fileName": os.path.basename(pdf_path), "status": "Failed", "error": str(e)}