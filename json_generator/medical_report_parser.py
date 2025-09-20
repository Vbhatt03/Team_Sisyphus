import os
import json
import requests
import re
import fitz  # PyMuPDF

# --- Configuration ---
# --- IMPORTANT: Paste your free OCR.space API key here ---
# Get your key from https://ocr.space/
OCR_SPACE_API_KEY = "K88629238088957" # This is a public test key, please get your own

# --- File Paths ---
INPUT_PDF = "D:\\Goa_p_hackathon\\victim report to PDF 20250907 12.57.07.pdf"
OUTPUT_JSON = "victim_report.json"
MAX_PAGES_PER_BATCH = 3  # Max 3 pages per API call on the free tier

def run_ocr_space_on_pages(pdf_path, start_page, end_page):
    """Convert selected pages to images and send to OCR.space API."""
    text_blocks = []
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    end_page = min(end_page, total_pages)
    
    print(f"Processing pages {start_page + 1} to {end_page}...")
    for page_num in range(start_page, end_page):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300) # Higher DPI for better accuracy
        img_bytes = pix.tobytes("png")
        
        resp = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("page.png", img_bytes, "image/png")},
            data={
                "apikey": OCR_SPACE_API_KEY,
                "OCREngine": 2, # Use the more advanced engine
                "isOverlayRequired": False,
                "language": "eng"
            },
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("IsErroredOnProcessing"):
            raise Exception(f"OCR.space error: {result.get('ErrorMessage')}")
        
        # Concatenate text from the parsed results
        if result.get("ParsedResults"):
            text_blocks.append(result["ParsedResults"][0].get("ParsedText", ""))
    
    doc.close()
    return "\n\n".join(text_blocks)

def extract_text_from_pdf_in_batches(pdf_path):
    """Extract text from PDF in batches to respect API limits."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file was not found at the specified path: {pdf_path}")
        
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    full_text = []
    for start in range(0, total_pages, MAX_PAGES_PER_BATCH):
        end = start + MAX_PAGES_PER_BATCH
        batch_text = run_ocr_space_on_pages(pdf_path, start, end)
        full_text.append(batch_text)
    
    return "\n\n".join(full_text)

def parse_victim_report(text):
    """
    Parse victim medical report with comprehensive, OCR-tolerant regex, 
    preventing overcapture by using section-based parsing.
    """
    data = {"report_type": "Victim Medico-Legal Examination"}

    # Helper function to find a value using regex, with a default
    def find_value(pattern, search_text, group=1, default=None):
        match = re.search(pattern, search_text, re.IGNORECASE | re.DOTALL)
        # Clean up common OCR artifacts and extra whitespace
        return ' '.join(match.group(group).strip().split()) if match else default

    # --- Section-based parsing helper ---
    def get_section(start_pattern, end_pattern, search_text):
        match = re.search(f"{start_pattern}(.*?){end_pattern}", search_text, re.DOTALL | re.IGNORECASE)
        # If a section is not found, return an empty string to avoid errors
        return match.group(1) if match else ""

    # --- 1. Header Information (Page 1) ---
    header_text = get_section(r"Medico-legal Examination Report", r"13\.\s*Marks of identification", text)
    data["sr_no"] = find_value(r"Sr\.?\s*No\.?\s*[:\-]?\s*([A-Z0-9\/]+)", header_text)
    data["name"] = find_value(r"Name\s*2\.\s*(.+?)\s*3\.", header_text)
    data["address"] = find_value(r"Address\s*3\.\s*(.+?)\s*4\.", header_text)
    data["age"] = find_value(r"Age\s*\(as reported\)\s*(.+?)\s*Date of Birth", header_text)
    data["date_of_birth"] = find_value(r"Date of Birth\s*\(it known\)\.?\s*([\d\/\.]+)", header_text)
    data["sex"] = find_value(r"Sex\s*\(M/F/Others\)\s*(.+?)\s*6\.", header_text)
    data["arrival_datetime"] = find_value(r"arrival in the hospital\s*(.+?)\s*7\.", header_text)
    data["examination_datetime"] = find_value(r"commencement of examination\s*(.+?)\s*8\.", header_text)
    data["brought_by"] = find_value(r"Brought by\s*(.+?)\s*9\.", header_text)
    data["mlc_no"] = find_value(r"MLC No\.?\s*([\d\.\/]+)", header_text)
    data["police_station"] = find_value(r"Police Station\s*(.+?)\s*10\.", header_text)
    
    # --- 13. Marks of Identification ---
    id_marks_text = get_section(r"13\.\s*Marks of identification", r"14\.\s*Relevant Medical", text)
    id_marks = re.findall(r"\(\d+\)\s*(.+)", id_marks_text)
    data["identification_marks"] = [mark.strip() for mark in id_marks] if id_marks else None
    
    # --- 15A. History of Sexual Violence ---
    history_text = get_section(r"15 A\.History of Sexual Violence", r"15 B\.", text)
    data["history_of_violence"] = {
        "date_of_incident": find_value(r"Date of incident's being reported\s*([\d\s,/&]+)", history_text),
        "location": find_value(r"Location/s\s*(\w+)", history_text),
        "number_of_assailants": find_value(r"Number of Assailant\(s\)\s*and\s*name/s\.\s*(\w+)", history_text),
        "assailant_name": find_value(r"Number of Assailant\(s\)\s*and\s*name/s\.\s*\w+\s*(.+)", history_text),
        "assailant_relationship": find_value(r"relationship with the survivor\s*(.+)", history_text),
        "narrative": find_value(r"Description of incident in the words of the narrator:\s*(.+)", history_text, default="Not clearly captured.")
    }

    # --- 15F. Details regarding sexual violence (Checkboxes and Tables) ---
    violence_details_text = get_section(r"15 F\. Details regarding sexual violence", r"Post incident has the survivor", text)
    data["sexual_violence_details"] = {
        "penetration_genitalia_penis": "Yes" if re.search(r"Genitalia\s*\(Vagina.*?Yes", violence_details_text, re.DOTALL) else "No",
        "emission_of_semen": "Yes" if re.search(r"Emission of Semen\s*Yes", violence_details_text) else "No",
        "post_incident_actions": {
            "changed_clothes": find_value(r"Changed clothes\s*([Yy]es|[Nn]o)", text),
            "bathed": find_value(r"Bathed\s*([Yy]es|[Nn]o)", text),
            "passed_urine": find_value(r"Passed urine\s*([Yy]es|[Nn]o)", text),
        }
    }
    
    # --- 16. General Physical Examination ---
    general_exam_text = get_section(r"16\. General Physical Exantination", r"17\. Examination for injuries", text)
    data["general_physical_examination"] = {
        "pulse": find_value(r"Pulse\.\s*([\d\/bpm]+)", general_exam_text),
        "bp": find_value(r"BP\s*([\d\/]+)", general_exam_text),
        "height_cm": find_value(r"Height:\s*(\d+)", general_exam_text),
        "weight_kg": find_value(r"Weight\s*(\d+)", general_exam_text),
    }

    # --- 18. Local Examination of Genital Parts ---
    genital_exam_text = get_section(r"18\. Local examination of genital parts", r"19\. Systemic examination", text)
    data["genital_examination_findings"] = {
        "external_genitalia": find_value(r"External Genitalla\s*(.*?)\*", genital_exam_text),
        "hymen": find_value(r"Hymen Perineum\s*(.+)", genital_exam_text),
        "anus_and_rectum": find_value(r"Anus and Rectum\s*\((.*?)\)", genital_exam_text),
        "oral_cavity": find_value(r"Oral Cavity\s*-\s*\((.*?)\)", genital_exam_text)
    }

    # --- 21. Samples Collected for FSL ---
    samples_text = get_section(r"21\. Samples Collection for Central", r"22\. Provisional medical opinion", text)
    collected_samples = []
    if re.search(r"Vulval swabs\s*Collected", samples_text, re.IGNORECASE): collected_samples.append("Vulval swabs")
    if re.search(r"Vaginal swabs\s*Collected", samples_text, re.IGNORECASE): collected_samples.append("Vaginal swabs")
    if re.search(r"Vaginal smear\s*Collected", samples_text, re.IGNORECASE): collected_samples.append("Vaginal smear")
    if re.search(r"Blood for grouping.*?\s*Collected", samples_text, re.DOTALL | re.IGNORECASE): collected_samples.append("Blood for grouping")
    data["samples_collected_fsl"] = collected_samples if collected_samples else None

    # --- 22. Provisional Medical Opinion ---
    opinion_text = get_section(r"22\. Provisional medical opinion", r"23\. Treatment prescribed", text)
    data["provisional_medical_opinion"] = find_value(r"Provisional\s*medical\s*opinion\s*(.+)", opinion_text)

    # --- 23. Treatment Prescribed ---
    treatment_text = get_section(r"23\. Treatment prescribed", r"24\. Date and time of completion", text)
    treatments = []
    if re.search(r"STI prevention treatment\s*Yes", treatment_text, re.IGNORECASE): treatments.append("STI prevention treatment")
    if re.search(r"Counselling\s*Yes", treatment_text, re.IGNORECASE): treatments.append("Counselling")
    data["treatment_prescribed"] = treatments if treatments else None

    return data

def main():
    try:
        # Step 1: Extract text in batches using OCR.space API
        print(f"Starting OCR process for {INPUT_PDF}...")
        text = extract_text_from_pdf_in_batches(INPUT_PDF)
        if not text or not text.strip():
            print(f"No text could be extracted from {INPUT_PDF}. Please check the file or API key.")
            return

        # Step 2: Parse the extracted text
        print("OCR text extracted successfully. Parsing structured data...")
        parsed_data = parse_victim_report(text)

        # Step 3: Save the final JSON
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)

        print(f"\nProcess completed successfully!")
        print(f"Victim report structured data has been saved to {OUTPUT_JSON}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: A network error occurred while contacting the OCR.space API: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

