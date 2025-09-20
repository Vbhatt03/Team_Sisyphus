import os
import json
import requests
import re
import fitz  # PyMuPDF

OCR_SPACE_API_KEY = "K88629238088957"
INPUT_PDF_PATH = 'D:\\Goa_p_hackathon\\fir_report_compressed.pdf'
OUTPUT_JSON = 'D:\\Goa_p_hackathon\\fir_data.json'
MAX_PAGES_PER_BATCH = 3  # Max 3 pages per API call

def run_ocr_space_on_pages(pdf_path, start_page, end_page):
    """Convert selected pages to images and send to OCR.space API."""
    text_blocks = []
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    end_page = min(end_page, total_pages)
    
    for page_num in range(start_page, end_page):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        
        resp = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("page.png", img_bytes, "image/png")},
            data={
                "apikey": OCR_SPACE_API_KEY,
                "OCREngine": 2,
                "isOverlayRequired": False,
                "language": "eng"
            },
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("IsErroredOnProcessing"):
            raise Exception(f"OCR.space error: {result.get('ErrorMessage')}")
        
        # Concatenate text
        text_blocks.append(result["ParsedResults"][0].get("ParsedText", ""))
    
    doc.close()
    return "\n\n".join(text_blocks)

def extract_text_from_pdf_in_batches(pdf_path):
    """Extract text from PDF in batches of MAX_PAGES_PER_BATCH."""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    full_text = []
    for start in range(0, total_pages, MAX_PAGES_PER_BATCH):
        end = start + MAX_PAGES_PER_BATCH
        batch_text = run_ocr_space_on_pages(pdf_path, start, end)
        full_text.append(batch_text)
    
    return "\n\n".join(full_text)

def parse_fir_data(text):
    """Parse FIR text into structured JSON with OCR-tolerant fallbacks."""
    data = {}

    # 1️⃣ FIR basic details (police station, year, FIR no, date)
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
        data.update({'police_station': None, 'year': None, 'fir_no': None, 'fir_date': None})

    # 1b️⃣ Fallback: extract police station and FIR from narrative if top lines failed
    if not data['police_station'] or not data['fir_no']:
        ps_match = re.search(r"(\b[A-Z][a-zA-Z\s]+)\s+PS", text)
        fir_no_match = re.search(r"Cr\.?\s*No\.?\s*([\d\/]+)", text, re.IGNORECASE)
        if ps_match and not data['police_station']:
            data['police_station'] = ps_match.group(1).strip()
        if fir_no_match and not data['fir_no']:
            data['fir_no'] = fir_no_match.group(1).strip()
        # Try to extract year from FIR number if missing
        if not data['year'] and data.get('fir_no'):
            year_match = re.search(r"(\d{4})", data['fir_no'])
            if year_match:
                data['year'] = year_match.group(1)

    # 2️⃣ Acts and Sections
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

    # 3️⃣ Complainant/Informant
    complainant_block_match = re.search(r"6\s+Complainant.*?Informan(.*?)\n7\s+Details", text, re.DOTALL | re.IGNORECASE)
    if complainant_block_match:
        block = complainant_block_match.group(1).strip()
        # Attempt to extract name & address if present
        name_match = re.search(r"Name\s*[:\-]\s*(.+)", block, re.IGNORECASE)
        addr_match = re.search(r"Address\s*[:\-]\s*(.+)", block, re.IGNORECASE)
        data['complainant_informant'] = {
            "name": name_match.group(1).strip() if name_match else "null",
            "address": addr_match.group(1).strip() if addr_match else "null"
        }
    else:
        data['complainant_informant'] = {"name": None, "address": None}

    # 4️⃣ Accused Details
    accused_match = re.search(r"7\s+Details.*?Unknown", text, re.DOTALL | re.IGNORECASE)
    if accused_match:
        data['accused_details'] = [{"name": "Unknown", "address": "Unknown"}]
    else:
        data['accused_details'] = []

    # 5️⃣ Brief Facts
    facts_match = re.search(r"12\s+First\s+Information\s+contents.*?\(Brief Facts\)\s*[\r\n]+(.*?)\n13\s+Action\s+Taken",
                            text, re.DOTALL | re.IGNORECASE)
    data['brief_facts'] = facts_match.group(1).replace('\n', ' ').strip() if facts_match else None

    # 6️⃣ FIR Date fallback: look for "Dated" anywhere if still missing
    if not data.get('fir_date'):
        date_match = re.search(r"Dated\s*[:\-]?\s*([\d\/\-]+)", text, re.IGNORECASE)
        if date_match:
            data['fir_date'] = date_match.group(1).strip()

    return data

def main():
    try:
        # OCR in batches
        text = extract_text_from_pdf_in_batches(INPUT_PDF_PATH)
        if not text.strip():
            print(f"No text extracted from {INPUT_PDF_PATH}")
            return

        # Parse FIR fields
        parsed_data = parse_fir_data(text)
        parsed_data['source_pdf'] = os.path.basename(INPUT_PDF_PATH)

        # Save JSON
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump([parsed_data], f, indent=4, ensure_ascii=False)

        print(f"FIR structured data saved to {OUTPUT_JSON}")

    except Exception as e:
        print(f"Error processing {INPUT_PDF_PATH}: {e}")

if __name__ == "__main__":
    main()
