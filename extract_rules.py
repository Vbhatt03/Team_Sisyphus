# save as extract_rules.py
import re
import json
import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
import tempfile

# Install: pip install pdfplumber pytesseract pillow regex

def parse_timeline(text: str) -> Optional[int]:
    text = (text or "").lower()
    if not text.strip(): 
        return None
    if any(k in text for k in ["immediately", "promptly", "at the earliest", "without any delay"]):
        return None
    m = re.search(r"within\s+(\d+)\s*hour", text)
    if m:
        return int(m.group(1))
    m = re.search(r"within\s+(\d+)\s*day", text)
    if m:
        return int(m.group(1)) * 24
    # phrases like 'twenty four hours' -> 24
    m = re.search(r"within\s+([a-z -]+)\s*hours?", text)
    if m:
        # convert words to numbers (basic)
        words = m.group(1).replace('-', ' ')
        word_to_num = {
            "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,
            "eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,
            "eighteen":18,"nineteen":19,"twenty":20,"twenty four":24,"twenty four":24
        }
        for k,v in word_to_num.items():
            if k in words:
                return v
    return None

def extract_bprd_table(bprd_pdf_path: str) -> List[Dict]:
    rules = []
    with pdfplumber.open(bprd_pdf_path) as pdf:
        # pages 3 through 15 are 0-indexed pages 2..14
        for i in range(2, min(len(pdf.pages), 15)):
            page = pdf.pages[i]
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []
            for table in tables:
                # Expect columns: Sl. No., Proceedings, Suggested time limit
                for row in table[1:]:
                    if len(row) < 3:
                        continue
                    sl, proceedings, suggested = row[0], row[1] or "", row[2] or ""
                    # create object
                    timeline = parse_timeline(suggested)
                    obj = {
                        "raw_sl": sl,
                        "procedure": (proceedings.strip()[:200] if proceedings else ""),
                        "details": (proceedings.strip() if proceedings else ""),
                        "legal_ref": None,
                        "timeline_hours": timeline,
                        "source_doc": "BPR&D SOP",
                        "category": None
                    }
                    rules.append(obj)
    return rules

def ocr_pdf_to_text(pdf_path: str) -> str:
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # render page to image then OCR to handle scanned PDFs
            pil_img = page.to_image(resolution=200).original
            text = pytesseract.image_to_string(pil_img)
            texts.append(text)
    return "\n".join(texts)

def extract_rules_from_text(text: str, source_doc: str) -> List[Dict]:
    rules = []
    # split into candidate sentences
    sentences = re.split(r'(?<=[\.\n])\s+', text)
    patterns = [
        r"within\s+\d+\s*(?:hours|hour|days|day)",
        r"preferably\s+within\s+\w+\s*hours",
        r"shall\s+be\s+done\s+at\s+the\s+earliest",
        r"within\s+[a-z -]+hours",
        r"within\s+sixty\s+days",
        r"within\s+60\s*days"
    ]
    regex = re.compile("|".join(patterns), re.IGNORECASE)
    for i,s in enumerate(sentences):
        if regex.search(s):
            timeline = parse_timeline(s)
            # capture some surrounding context
            context = s
            if i>0:
                context = sentences[max(0,i-1)] + " " + context
            if i+1 < len(sentences):
                context = context + " " + sentences[i+1]
            # try to find legal ref like 'U/s 164 Cr.P.C.' or 'Section 164-A' or 'POCSO'
            legal = None
            m = re.search(r"(section\s+\d+[A-Za-z\-]*\s*cr\.p\.c\.|u\/s\.?\s*\d+\s*cr\.p\.c\.|164-a|164\s*cr\.p\.c\.|pocso|criminal law \(amendment\) act,? 2018)", context, re.IGNORECASE)
            if m:
                legal = m.group(0).strip()
            # make a short procedure summary by extracting first clause up to comma
            proc = context.strip().split('.')[0].strip()
            rules.append({
                "procedure": proc,
                "details": context.strip(),
                "legal_ref": legal,
                "timeline_hours": timeline,
                "source_doc": source_doc,
                "category": None
            })
    return rules

def dedupe_and_assign_ids(rules: List[Dict]) -> List[Dict]:
    out = []
    seen = {}
    def make_id(procedure):
        s = re.sub(r'[^A-Z0-9]+', '_', procedure.upper())[:30].strip('_')
        return s or "STEP"
    for r in rules:
        key = (r.get("procedure","").lower().strip())
        if not key:
            continue
        if key in seen:
            # merge details preferring longer details
            existing = seen[key]
            if len(r.get("details","")) > len(existing["details"]):
                existing["details"] = r["details"]
            if existing.get("timeline_hours") is None and r.get("timeline_hours") is not None:
                existing["timeline_hours"] = r["timeline_hours"]
            # prefer legal_ref if missing
            if not existing.get("legal_ref") and r.get("legal_ref"):
                existing["legal_ref"] = r["legal_ref"]
            # prefer source_doc 'Delhi Police SOP' when merging
            if r.get("source_doc") == "Delhi Police SOP":
                existing["source_doc"] = r["source_doc"]
            continue
        # new
        sid = make_id(r.get("procedure",""))
        # ensure uniqueness
        base = sid
        i = 1
        while any(x["step_id"]==sid for x in out):
            i += 1
            sid = f"{base}_{i}"
        entry = {
            "step_id": sid,
            "procedure": r.get("procedure",""),
            "details": r.get("details",""),
            "legal_ref": r.get("legal_ref"),
            "timeline_hours": r.get("timeline_hours") if r.get("timeline_hours") is not None else None,
            "source_doc": r.get("source_doc"),
            "category": r.get("category") or categorize_rule(r.get("procedure","") + " " + r.get("details",""))
        }
        out.append(entry)
        seen[key] = entry
    return out

def categorize_rule(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["fir", "register", "registration", "complaint"]):
        return "FIR"
    if any(k in t for k in ["medical", "examination", "doctor", "hospital"]):
        return "Medical"
    if any(k in t for k in ["evidence", "sample", "collection", "seize", "preserve"]):
        return "Evidence Collection"
    if any(k in t for k in ["164", "statement", "recorded", "statement of the victim"]):
        return "Legal/Statement"
    if any(k in t for k in ["charge sheet", "file", "investigation completed", "60 days"]):
        return "Reporting"
    return "Other"

def main(bprd_pdf, delhi_pdf, out_json="rules.json"):
    all_rules = []
    # BPR&D table extraction
    if Path(bprd_pdf).exists():
        bprd_rules = extract_bprd_table(bprd_pdf)
        for r in bprd_rules:
            r["source_doc"] = "BPR&D SOP"
            # map timeline already set
            all_rules.append(r)
    # Delhi OCR
    if Path(delhi_pdf).exists():
        txt = ocr_pdf_to_text(delhi_pdf)
        delhi_rules = extract_rules_from_text(txt, "Delhi Police SOP")
        all_rules.extend(delhi_rules)
    # dedupe and assign ids
    final = dedupe_and_assign_ids(all_rules)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(final)} rules to {out_json}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract rules from BPR&D and Delhi Police SOP PDFs.")
    parser.add_argument("--bprd_pdf", type=str, required=True, help="Path to BPR&D SOP PDF file")
    parser.add_argument("--delhi_pdf", type=str, required=True, help="Path to Delhi Police SOP PDF file")
    parser.add_argument("--out_json", type=str, default="Team_Sisyphus\\rules.json", help="Output JSON file path")
    args = parser.parse_args()
    main(args.bprd_pdf, args.delhi_pdf, args.out_json)
