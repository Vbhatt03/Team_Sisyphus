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
import re

def parse_fir_data(text: str) -> dict:
    """
    Parses FIR text into a structured JSON using regular expressions.
    This function is designed to be a self-contained module for detection and writing.
    """
    data = {}

    # Helper to clean extracted strings
    def clean(value):
        return value.strip() if value else None

    # 1. FIR Basic Details (Section 1)
    # This regex looks for the specific labels in the header of the FIR.
    fir_details_match = re.search(
        r"District:\s*(?P<district>.*?)\s*P\.S\.:\s*(?P<ps>.*?)\s*Year:\s*(?P<year>\d{4})\s*FIR No\.\s*(?P<fir_no>[\d\/]+)\s*Date:\s*(?P<date>[\d\-]+)\s*Time:\s*(?P<time>[\d\:]+)",
        text, re.DOTALL
    )
    if fir_details_match:
        data['fir_details'] = {k: clean(v) for k, v in fir_details_match.groupdict().items()}

    # 2. Acts and Sections (Section 2)
    # First, isolate the text block between "Act and Sections:" and "3.".
    acts_section_block = re.search(r"Act and Sections:\s*([\s\S]*?)\s*3\.", text)
    if acts_section_block:
        # Then, find all lines that look like "Act Name", "Section Number"
        matches = re.findall(r'"(.*?)"\s*,\s*"([^"]+)"', acts_section_block.group(1))
        data['acts_and_sections'] = [{'act': clean(act), 'section': clean(sec)} for act, sec in matches]

    # 3. Complainant / Informant (Section 6)
    # Isolate the block between "Complainant/Informant" and the next section "7."
    # Corrected logic for Complainant / Informant (Section 6)
    complainant_block_match = re.search(r"6\.\s*Complainant/Informant\s*([\s\S]*?)7\.", text)
    if complainant_block_match:
        complainant_text = complainant_block_match.group(1)
        details = {}
        
        # Define a list of the fields we expect to find in this section.
        fields_to_find = [
            'Name', 'Relation', 'Nationality', 'Occupation', 
            'Date of Birth', 'Age', 'Present Address', 'Permanent Address'
        ]
        
        for field in fields_to_find:
            # This more flexible regex finds the field name and then captures the value
            # that follows, handling variations in newlines, commas, and quotes.
            # It looks for the field, then potential junk characters, then captures the clean value.
            pattern = re.compile(rf'{field}\s*(?:[",\s]*\n)?[",\s]*([^\n"]+)', re.IGNORECASE)
            match = pattern.search(complainant_text)
            
            if match:
                # We found the field, now we extract its value.
                value = match.group(1).strip()
                field_name = field.lower().replace(' ', '_').replace('/', '_')
                details[field_name] = clean(value) # Assumes your 'clean' function exists
                
        data['complainant_informant'] = details

    # 4. Accused Details (Section 7)
    # Isolate the block between the "accused" heading and the next section "8."
    accused_block = re.search(r"7\.\s*Details of Known / Suspected / Unknown accused.*?([\s\S]*?)8\.", text)
    if accused_block:
        details = {}
        # Find key-value pairs, which are more loosely structured in this section
        matches = re.findall(r"([A-Za-z\s/]+)\s*\n+\s*([^\n]+)", accused_block.group(1))
        # This part is more complex due to OCR variations
        raw_text = accused_block.group(1)
        details['name'] = clean(re.search(r'Name of Accused\s*([^\n]+)', raw_text, re.I).group(1) if re.search(r'Name of Accused\s*([^\n]+)', raw_text, re.I) else None)
        details['relation'] = clean(re.search(r'Relation\s*([^\n]+)', raw_text, re.I).group(1) if re.search(r'Relation\s*([^\n]+)', raw_text, re.I) else None)
        details['nationality'] = clean(re.search(r'Nationality\s*([^\n]+)', raw_text, re.I).group(1) if re.search(r'Nationality\s*([^\n]+)', raw_text, re.I) else None)
        details['occupation'] = clean(re.search(r'Occupation\s*([^\n]+)', raw_text, re.I).group(1) if re.search(r'Occupation\s*([^\n]+)', raw_text, re.I) else None)
        details['present_address'] = clean(re.search(r'Present Address\s*([^\n]+)', raw_text, re.I).group(1) if re.search(r'Present Address\s*([^\n]+)', raw_text, re.I) else None)
        details['permanent_address'] = clean(re.search(r'Permanent Address\s*([^\n]+)', raw_text, re.I).group(1) if re.search(r'Permanent Address\s*([^\n]+)', raw_text, re.I) else None)
        details['age'] = clean(re.search(r'Age\s*([^\n]+)', raw_text, re.I).group(1).replace('(Approx.)','').strip() if re.search(r'Age\s*([^\n]+)', raw_text, re.I) else None)
        data['accused_details'] = details


    # 5. Brief Facts / Narrative (Section 12)
    # Capture the narrative between "First Information contents" and the next section "13."
    brief_facts = re.search(r"12\.\s*First Information contents \(Brief Facts\)\s*([\s\S]*?)13\.\s*Action Taken", text)
    if brief_facts:
        # Join lines into a single, clean paragraph
        narrative = ' '.join(brief_facts.group(1).strip().split())
        data['brief_facts'] = narrative

    # 6. Action and Officer Details (Section 13)
    # Isolate the final action block to find officer details
    action_block = re.search(r"13\.\s*Action Taken([\s\S]*?)14\.", text)
    if action_block:
        io_details = re.search(r"Directed \(Name of I\.O\.\)\s*(?P<name>.*?)\s*Rank:\s*(?P<rank>.*?)\s*No\.\s*(?P<no>\d+)", action_block.group(1))
        if io_details:
            data['investigating_officer'] = {
                'name': clean(io_details.group('name')),
                'rank': clean(io_details.group('rank')),
                'number': clean(io_details.group('no')),
            }
    
    officer_in_charge = re.search(r"Signature of Officer in charge, Police Station\s*[\s\S]*?Name:\s*(?P<name>.*?)\s*Rank:\s*(?P<rank>.*?)\s*No\.:\s*(?P<no>\d+)", text, re.DOTALL)
    if officer_in_charge:
        data['officer_in_charge'] = {
            'name': clean(officer_in_charge.group('name')),
            'rank': clean(officer_in_charge.group('rank')),
            'number': clean(officer_in_charge.group('no')),
        }
        
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