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

# --- NEW, FORMAT-SPECIFIC PARSING LOGIC ---

def parse_detail(text, pattern, group=1):
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
    cleaned_text = re.sub(r'\s+', ' ', match.group(group).replace('\n', ' ').replace('\r', ''))
    return cleaned_text.strip()

def parse_victim_report(text):
    """Parses a victim's medical report based on the provided format."""
    logging.info("Parsing document as Victim Medico-Legal Report.")
    
    # Extract name and OPD separately, then combine or handle as needed
    name_opd_str = parse_detail(text, r"Name/OPD No\.:\s*(.*?)(?=\n)")
    name, opd_no = (name_opd_str.split('/', 1) + [None])[:2]
    
    # Extract samples using a more robust method
    samples_section = parse_detail(text, r"Sample Collection\s*(.*?)(?=Provisional Medical Opinion)")
    samples_collected = []
    if samples_section:
        # Find all lines that seem to list a collected item
        potential_samples = re.findall(r"•\s*([^\n\r]+)", samples_section)
        samples_collected = [s.strip() for s in potential_samples]

    data = {
        "report_type": "Victim Medico-Legal Examination",
        "sr_no": parse_detail(text, r"Sr\. No\.:\s*(\S+)"),
        "name": name.strip() if name else None,
        "opd_no": opd_no.strip() if opd_no else None,
        "age": parse_detail(text, r"Age as reported:\s*([\d\s]+\w+)"),
        "address": parse_detail(text, r"Address:\s*([^\n\r]+)"),
        "mlc_no": parse_detail(text, r"MLC No\.:\s*(\S+)"),
        "police_station": parse_detail(text, r"Police Station:\s*([^\n\r]+)"),
        "arrival_datetime": parse_detail(text, r"arrival in the hospital:\s*(.*)"),
        "examination_datetime": parse_detail(text, r"commencement of examination:\s*(.*)"),
        "history_of_violence": parse_detail(text, r"History of Sexual Violence.*?Description:\s*(.*?)(?=Physical & Genital Examination)"),
        "genital_examination_findings": parse_detail(text, r"Genitalia:\s*(.*?)(?=Sample Collection)"),
        "provisional_medical_opinion": parse_detail(text, r"Provisional Medical Opinion\s*(.*?)(?=Date:)"),
        "samples_collected": samples_collected
    }
    return data

def parse_accused_report(text):
    """Parses an accused's medical report based on the provided format."""
    logging.info("Parsing document as Accused Medical Examination Report.")

    # Combine Date and Time for a full examination timestamp
    exam_date = parse_detail(text, r"Date:\s*(\d{2}/\d{2}/\d{4})")
    exam_time = parse_detail(text, r"Time:\s*(\d{2}:\d{2}\s*[AP]M)")
    exam_datetime = f"{exam_date}, {exam_time}" if exam_date and exam_time else None

    data = {
        "report_type": "Accused Medical Examination in Sexual Offences",
        "sr_no": parse_detail(text, r"Sr\. No\.:\s*(\S+)"),
        "crime_no": parse_detail(text, r"Crime No\.:\s*([^\n\r]+)"),
        "name": parse_detail(text, r"Name:\s*([^\n\r]+)"),
        "residence": parse_detail(text, r"Residence:\s*([^\n\r]+)"),
        "age": parse_detail(text, r"Age:\s*([\d\s]+\w+)"),
        "examination_datetime": exam_datetime,
        "injuries_on_body": parse_detail(text, r"Injuries on the body:\s*(.*?)(?=GENITAL EXAMINATION)"),
        "genital_examination_findings": parse_detail(text, r"GENITAL EXAMINATION:\s*(.*?)(?=OPINION:)"),
        "opinion": parse_detail(text, r"OPINION:\s*(.*?)(?=Samples collected:)"),
        "samples_collected": parse_detail(text, r"Samples collected:\s*(.*)")
    }
    return data

def process_medical_pdf(pdf_path, api_key):
    """
    Main orchestrator function that extracts text, determines the report type,
    parses the data, and redacts sensitive information.
    """
    logging.info(f"Processing Medical Report: {os.path.basename(pdf_path)}")
    
    try:
        full_ocr_text = extract_text_from_pdf_in_batches(pdf_path, api_key)

        if not full_ocr_text:
            logging.warning(f"No text extracted from {pdf_path}. Cannot generate report.")
            return {"fileName": os.path.basename(pdf_path), "error": "No text could be extracted."}

        # Determine report type and call the appropriate parser
        parsed_data = {}
        if "Report of Medical Examination in Sexual Offences for Males" in full_ocr_text:
            parsed_data = parse_accused_report(full_ocr_text)
        elif "Medico-Legal Examination Report of Sexual Violence" in full_ocr_text:
            parsed_data = parse_victim_report(full_ocr_text)
        else:
            logging.warning(f"Could not determine the report type for {os.path.basename(pdf_path)}.")
            return {"fileName": os.path.basename(pdf_path), "error": "Unknown report format."}
        
        # --- SENSITIVE DATA REDACTION ---
        # Redact sensitive fields to null (None in Python) to ensure privacy.
        logging.info("Redacting sensitive personal information (name, age, address/residence).")
        parsed_data["name"] = None
        parsed_data["age"] = None
        # Handle both 'address' and 'residence' keys for redaction
        if "address" in parsed_data:
            parsed_data["address"] = None
        if "residence" in parsed_data:
            parsed_data["residence"] = None
            
        return parsed_data

    except Exception as e:
        logging.error(f"A fatal error occurred while processing '{os.path.basename(pdf_path)}': {e}")
        return {"fileName": os.path.basename(pdf_path), "status": "Failed", "error": str(e)}