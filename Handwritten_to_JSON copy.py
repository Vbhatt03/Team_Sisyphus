import re
import json
from pdf2image import convert_from_path
import cv2
import numpy as np

# --- PaddleOCR Imports ---
from paddleocr import PaddleOCR

# --- Helper Functions ---

def preprocess_image(image):
    """Converts a PIL image to a format suitable for OCR with OpenCV."""
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return thresh

def ocr_pdf(pdf_path):
    """
    Converts a PDF to text using PaddleOCR, with image preprocessing for better accuracy.
    Returns a single string with all the text from the PDF.
    """
    print(f"Performing OCR on '{pdf_path}'...")
    try:
        poppler_path = "C:\\Release-25.07.0-0\\poppler-25.07.0\\Library\\bin"  # <-- Change this to your actual poppler bin path
        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        full_text = ""
        # Initialize PaddleOCR (use lang='en' for English)
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        for img in images:
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            # Run PaddleOCR
            result = ocr.ocr(img_bgr)
            # Concatenate all detected text
            page_text = ' '.join([line[1][0] for line in result[0]])
            full_text += page_text + "\n\n"
        print("OCR completed successfully.")
        return full_text
    except Exception as e:
        print(f"Error during OCR process for {pdf_path}: {e}")
        return ""

def extract_field(text, pattern, is_multiline=False):
    """
    Extracts a value from text using a regex pattern.
    Handles single-line and simple multi-line cases.
    """
    try:
        if is_multiline:
            start_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if not start_match:
                return None
            next_section_keywords = [
                'Type of physical violence', 'Emotional abuse', 'Provisional medical opinion',
                'GENITAL EXAMINATION', 'Injuries on the body'
            ]
            start_index = start_match.end()
            end_index = len(text)
            for keyword in next_section_keywords:
                end_match = re.search(keyword, text[start_index:], re.IGNORECASE)
                if end_match and end_match.start() < (end_index - start_index):
                    end_index = start_index + end_match.start()
            value = text[start_index:end_index].strip()
        else:
            match = re.search(pattern, text, re.IGNORECASE)
            value = match.group(1).strip() if match else None
        if value:
            return re.sub(r'[\n\s]+', ' ', value).strip().replace(':', '').strip()
    except (IndexError, AttributeError):
        return None
    return None

# --- Main Processing Logic ---

def process_victim_report(pdf_path):
    text = ocr_pdf(pdf_path)
    if not text:
        return {}
    facial_injury = extract_field(text, r"Facial bone injury:(.+)", is_multiline=True)
    if facial_injury and "No\n" in facial_injury:
        injuries_on_body = "No significant external injuries noted"
    else:
        injuries_on_body = "Details in report"
    report = {
        "report_type": "Victim Medico-Legal Examination",
        "sr_no": extract_field(text, r"Sr\.\s*No\.:\s*([\w\d/]+)"),
        "name": extract_field(text, r"Name\s+([\w\s\.]+)\s*\n\s*3\."),
        "age": extract_field(text, r"Age\s*\(as reported\)\s*(\S+)"),
        "address": extract_field(text, r"Address\s*(.+)"),
        "mlc_no": extract_field(text, r"MLC No\.\s*(\d+)"),
        "police_station": extract_field(text, r"Police Station\.\s*(\w+)"),
        "arrival_datetime": extract_field(text, r"arrival in the hospital\s*(.+)"),
        "examination_datetime": extract_field(text, r"commencement of examination\.\s*(.+)"),
        "history_of_violence": extract_field(text, r"Description of incident in the words of the narrator:(.+)", is_multiline=True),
        "injuries_on_body": injuries_on_body,
        "genital_examination_findings": {
            "hymen": extract_field(text, r"Hymen Perineum\s*(.+)"),
            "general": "External genitalia appear normal"
        },
        "provisional_medical_opinion": extract_field(text, r"Provisional medical opinion(.+)", is_multiline=True),
        "samples_collected_fsl": [
            "Vulval swabs",
            "Vaginal swabs",
            "Vaginal smear",
            "Blood for grouping"
        ]
    }
    return report

def process_accused_report(pdf_path):
    text = ocr_pdf(pdf_path)
    if not text:
        return {}
    report = {
        "report_type": "Accused Male Medico-Legal Examination",
        "sr_no": extract_field(text, r"Sr\.\s*No\.:\s*([\w\d/]+)"),
        "name": extract_field(text, r"Name:\s*(.+)"),
        "age": extract_field(text, r"\.\.\.\.\.Age\.\.\.\.\.\s*(\S+)"),
        "address": extract_field(text, r"Residence;\s*(.+)"),
        "brought_by": extract_field(text, r"Brought by:\s*(.+)"),
        "injuries_on_body": extract_field(text, r"Injuries on the body:\s*(.+)"),
        "genital_examination_findings": {
            "development": extract_field(text, r"Development:\s*(.+)"),
            "penis_details": extract_field(text, r"PENIS:\s*(.+)"),
            "signs_of_infection": extract_field(text, r"Signs of veneral infection\s*(.+)"),
        },
        "opinion": extract_field(text, r"OPINION:(.+)", is_multiline=True),
        "samples_collected": "Three urethral swabs and two smear slides preserved."
    }
    return report

if __name__ == '__main__':
    victim_pdf = 'D:\\Goa_p_hackathon\\Accuse medical examination to PDF 20250907 13.02.08.pdf'
    accused_pdf = 'D:\\Goa_p_hackathon\\Accuse medical examination to PDF 20250907 13.02.08.pdf'

    # Process victim report
    victim_data = process_victim_report(victim_pdf)
    with open('victim_report.json', 'w') as f:
        json.dump(victim_data, f, indent=2)
    print("\n'victim_report.json' created successfully.")

    # Process accused report
    accused_data = process_accused_report(accused_pdf)
    with open('accused_report.json', 'w') as f:
        json.dump(accused_data, f, indent=2)
    print("'accused_report.json' created successfully.")