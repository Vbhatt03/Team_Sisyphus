# medical_report_parser.py

"""
A reusable Python module to parse medical reports from PDF files.

This module is specifically designed to handle scanned documents containing both
typed and handwritten text by leveraging high-resolution image conversion and a
specialized Tesseract OCR configuration. It extracts structured data from
medical examination reports and returns it as a clean, hierarchical dictionary.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re
import io
import logging
from typing import Dict, Any, List

# Configure logging to display information about the parsing process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file by converting pages to images and using OCR.

    This function iterates through each page of the PDF, converts it into a
    high-resolution PNG image to improve OCR accuracy, and then uses the
    Tesseract OCR engine to extract text. It is specifically configured to
    handle layouts with mixed or handwritten fonts.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: A single string containing all the extracted text from the PDF.
             Returns an empty string if the file cannot be processed.
    """
    full_text = ""
    try:
        # Open the PDF file using PyMuPDF
        pdf_document = fitz.open(file_path)
        
        # Iterate over each page in the PDF
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Render the page to a high-resolution image (300 DPI) for better OCR
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            # Configure Tesseract for better handwriting and layout recognition
            # --oem 3: Use the LSTM OCR Engine (default, but good to be explicit).
            # --psm 6: Assume a single uniform block of text.
            custom_config = r'--oem 3 --psm 6'
            
            # Use pytesseract to extract text from the image
            text = pytesseract.image_to_string(image, config=custom_config)
            full_text += text + "\n"
            
        pdf_document.close()
        logging.info(f"Successfully extracted text from {file_path}")
        return full_text
    except Exception as e:
        logging.error(f"Failed to extract text from {file_path}: {e}")
        return ""

def _parse_structured_fields(text_content: str) -> Dict[str, Any]:
    """
    Parses raw text content to extract key-value pairs using regular expressions.

    This function uses a dictionary of predefined regex patterns to find and
    extract specific pieces of information from the raw OCR text. It is designed
    to be flexible and handle common OCR errors or variations in document layout.

    Args:
        text_content (str): The raw text extracted from the PDF.

    Returns:
        Dict[str, Any]: A dictionary containing the raw extracted data.
    """
    # Normalize text for easier regex matching
    text_content = re.sub(r'\s+', ' ', text_content).strip()

    # Dictionary of regex patterns to find different fields
    # Patterns are designed to be flexible with whitespace and separators (e.g., :, .)
    patterns = {
        # Report Details
        "serial_no": r"Sr\.\s*No\.\s*[:\s]*([\w/]+)",
        "examination_date": r"Date\s*[:\s]*(\d{2}/\d{2}/\d{2,4})",
        "examination_time": r"Time\s*[:\s]*(\d{2,4})\s*(am/pm)",
        "report_type_male": r"Sexual Offences for Males",
        "report_type_female": r"Medico-legal Examination Report of Sexual Violence",

        # Patient Details
        "name": r"Name\s*[:\s]*(.*?)(?:Age|Address|Caste|MARKS OF IDENTIFICATION)",
        "age": r"Age\s*(?:\(as reported\))?\s*[:\s]*(\d+)\s*yrs?",
        "dob": r"Date of Birth\s*(?:\(if known\))?\s*\.?\s*(\d{2}/\d{2}/\d{4})",
        "height": r"Height\s*[:\s]*(\d+)\s*cm",
        "weight": r"Weight\s*[:\s]*(\d+)\s*kg",

        # Findings and Opinions
        "injuries": r"Injuries on the body\s*[:\s]*(.*?)(?:GENITAL EXAMINATION|17\.)",
        "opinion": r"(?:OPINION|Provisional medical opinion)\s*[:\s]*(.*?)(?:Signature|Treatment prescribed|23\.)",
    }
    
    parsed_data = {}
    for key, pattern in patterns.items():
        # Use re.search to find the first match for each pattern
        match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
        if match:
            # If the pattern has a capturing group, extract it. Otherwise, store True.
            parsed_data[key] = match.group(1).strip() if match.groups() else True

    return parsed_data

def _clean_and_format_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans and structures the parsed data into a hierarchical format.

    This function takes the raw dictionary of extracted strings, cleans them up
    (e.g., trims whitespace), converts values to appropriate data types (int, float),
    and organizes them into a nested dictionary for clarity and ease of use.

    Args:
        parsed_data (Dict[str, Any]): The dictionary with raw parsed data.

    Returns:
        Dict[str, Any]: A clean, structured dictionary of the medical report data.
    """
    # Determine report type
    if parsed_data.get("report_type_male"):
        report_type = "Accused Male Examination Report"
    elif parsed_data.get("report_type_female"):
        report_type = "Victim Sexual Violence Report"
    else:
        report_type = "Unknown"

    # Clean and convert data types where possible
    def to_int(value):
        try:
            return int(re.search(r'\d+', value).group())
        except (AttributeError, TypeError, ValueError):
            return None

    # Construct the final structured dictionary
    final_report = {
        "report_details": {
            "report_type": report_type,
            "serial_number": parsed_data.get("serial_no"),
            "examination_date": parsed_data.get("examination_date"),
            "examination_time": f"{parsed_data.get('examination_time', '')} {parsed_data.get('am/pm', '')}".strip()
        },
        "patient_details": {
            "name": parsed_data.get("name"),
            "age": to_int(parsed_data.get("age", "")),
            "date_of_birth": parsed_data.get("dob"),
            "height_cm": to_int(parsed_data.get("height", "")),
            "weight_kg": to_int(parsed_data.get("weight", "")),
        },
        "findings": {
            "injuries": parsed_data.get("injuries", "No information found.").strip(),
            "opinion": parsed_data.get("opinion", "No information found.").strip()
        }
    }
    return final_report


def parse_medical_report(file_path: str) -> Dict[str, Any]:
    """
    Main entry point to parse a medical report PDF.

    This function orchestrates the entire parsing workflow:
    1. Extracts raw text from the PDF using OCR.
    2. Parses the raw text to find structured fields.
    3. Cleans and formats the extracted data into a final dictionary.

    Args:
        file_path (str): The absolute or relative path to the PDF medical report.

    Returns:
        Dict[str, Any]: A structured dictionary containing the parsed information
                        from the medical report. Returns an empty dictionary if
                        parsing fails at any stage.
    """
    logging.info(f"Starting parsing for report: {file_path}")
    
    # Step 1: Extract text using OCR
    raw_text = _extract_text_from_pdf(file_path)
    if not raw_text:
        logging.error("Text extraction failed. Aborting parse.")
        return {}

    # Step 2: Parse structured fields from raw text
    parsed_data = _parse_structured_fields(raw_text)
    if not parsed_data:
        logging.warning("Could not parse any structured fields from the text.")
        return {}

    # Step 3: Clean and format the data
    final_report = _clean_and_format_data(parsed_data)
    
    logging.info(f"Successfully parsed report: {file_path}")
    return final_report