# ==============================================================================
# NYAYA AI - FINAL REPORT & CHARGESHEET GENERATOR
# ===============================================================================
# This script performs the final steps of the pipeline:
# 1. Synthesizes a comprehensive Final Report for AI analysis from key sources.
# 2. Uses all case files and the AI-summary to generate an accurate,
#    auto-filled Chargesheet.
#
# Installation requirements:
# pip install numpy faiss-cpu sentence-transformers
# ===============================================================================

import json
import os
import re
import datetime
import textwrap
from typing import List, Optional, Dict, Any

# Optional ML imports. Code degrades gracefully if unavailable.
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


# ===============================================================================
# SECTION 1: CONFIGURATION - FILE PATHS
# ===============================================================================

# --- INPUT FILES ---
# NOTE: Update these paths to match your local file structure.
DATA_DIR = "json_generator\\output"
REPORT_DIR = "Report_generator\Outputs"

VICTIM_STATEMENT_FILE = os.path.join(DATA_DIR, "statement.json")
VICTIM_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "victim_med_rep.json")
ACCUSED_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "accused_med_rep.json")
FIR_FILE = os.path.join(DATA_DIR, "fir.json")

# This script now depends on the case diary from the other script
CASE_DIARY_FILE = os.path.join(REPORT_DIR, "case_diary.txt")

# --- OUTPUT FILES ---
FINAL_REPORT_FILE = os.path.join(REPORT_DIR, "final_report.txt")
CHARGESHEET_FILE = os.path.join(REPORT_DIR, "chargesheet.md")

# ===============================================================================
# SECTION 2: UTILITY FUNCTIONS
# ===============================================================================

def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Reads and safely parses a JSON file, returning None if invalid or not found."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                print(f"Warning: The file {file_path} is empty.")
                return None
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
        return None

def read_text_file(file_path: str) -> Optional[str]:
    """Reads a plain text file, returning None if not found."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The text file {file_path} was not found.")
        return None

def get_val(data: Dict[str, Any], key: str, default: Any = '[N/A]') -> Any:
    """Safely gets a value from a dictionary."""
    if not isinstance(data, dict):
        return '[Data unavailable]'
    val = data.get(key)
    return default if val is None or (isinstance(val, (str, list, dict)) and not val) else val

# ===============================================================================
# SECTION 3: REPORT & CHARGESHEET GENERATION
# ===============================================================================

def generate_final_report_for_ai(case_diary_text: str, statement_narrative: str, victim_medical_opinion: str, accused_medical_opinion: str) -> str:
    """Synthesizes a text report from key sources, optimized for AI analysis."""
    report = "FINAL INVESTIGATION REPORT (AI FEED)\n\n"
    report += "This document synthesizes information from the case diary, victim's full statement, and medical reports to provide a comprehensive narrative for analysis.\n"
    report += "==================================================================\n\n"
    report += "I. NARRATIVE FROM CASE DIARY\n--------------------------\n"
    report += case_diary_text + "\n\n"
    report += "II. FULL VICTIM STATEMENT\n--------------------------\n"
    report += statement_narrative + "\n\n"
    report += "III. MEDICAL OPINIONS\n--------------------------\n"
    report += f"Victim Medical Opinion: {victim_medical_opinion}\n"
    report += f"Accused Medical Opinion: {accused_medical_opinion}\n\n"
    report += "==================================================================\nEnd of Report\n"
    return report

def generate_chargesheet(final_report_text: str,
                         statement_data: dict,
                         accused_medical_data: dict,
                         victim_medical_data: dict,
                         fir_path: str,
                         additional_data: dict = None) -> str:
    """
    Generate a FORM IF5 style chargesheet.
    Data priority: statement_data > medical_data > FIR JSON > additional_data
    """
    fir_data = read_json_file(fir_path) or {}
    additional_data = additional_data or {}

    # ---------- Helpers ----------
    def _get_nested(d, keys, default="[N/A]"):
        cur = d
        for k in keys:
            if not isinstance(cur, dict): return default
            cur = cur.get(k, default)
        return cur if cur not in (None, "", [], {}) else default

    def _get_multi(paths, default="[N/A]"):
        sources = [statement_data, victim_medical_data, accused_medical_data, fir_data, additional_data]
        for path in (paths if isinstance(paths, list) else [paths]):
            for src in sources:
                val = _get_nested(src, path if isinstance(path, list) else [path], default=None)
                if val not in (None, "", [], {}): return val
        return default

    def _format_date(val, fmt="%d/%m/%Y"):
        if not val or val in ("[N/A]", None): return "[N/A]"
        if isinstance(val, (datetime.date, datetime.datetime)): return val.strftime(fmt)
        m = re.match(r"(\d{2})[-/.](\d{2})[-/.](\d{4})", str(val))
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else str(val)

    def _safe_paragraphs(text):
        return [p.strip() for p in re.split(r'\n+', text) if p.strip() and len(p.strip()) > 20]

    def _summarize_narrative(paragraphs, top_k=3):
        if not paragraphs: return "[Narrative missing]"
        if ML_AVAILABLE:
            try:
                model = SentenceTransformer("ai4bharat/indic-bert")
                emb_par = np.array(model.encode(paragraphs, show_progress_bar=False))
                emb_q = np.array(model.encode(["initial complaint sequence of events", "victim account", "medical findings", "how accused identified"], show_progress_bar=False))
                index = faiss.IndexFlatL2(emb_par.shape[1])
                index.add(emb_par.astype("float32"))
                _, I = index.search(emb_q.astype("float32"), k=min(2, len(paragraphs)))
                picked = [paragraphs[idx] for row in I for idx in row if idx >= 0]
                return "\n\n".join(dict.fromkeys(picked)) or paragraphs[0]
            except Exception as e:
                print(f"ML summarization failed: {e}. Falling back to basic summary.")
        return "\n\n".join(paragraphs[:top_k])

    def _format_dict_as_bullets(data, keys):
        lines = [f"- {k.replace('_',' ').title()}: {val}" for k in keys if (val := _get_nested(data, [k], None))]
        return "\n".join(lines) if lines else "[N/A]"

    def _build_medical_section(victim_md, accused_md):
        victim_keys = ["name", "age", "address", "history_of_violence", "genital_examination_findings", "provisional_medical_opinion"]
        accused_keys = ["name", "age", "opinion", "findings"]
        victim_block = _format_dict_as_bullets(victim_md, victim_keys)
        accused_block = _format_dict_as_bullets(accused_md, accused_keys)
        return f"Victim Medical/Expert Opinion:\n{textwrap.indent(victim_block, '  ')}\n\nAccused Medical/Expert Opinion:\n{textwrap.indent(accused_block, '  ')}"

    # ---------- Pull Data ----------
    now = datetime.datetime.now()
    crime_no = _get_multi([["case_info", "crime_no"], ["fir_details", "fir_no"]])
    police_station = _get_multi([["case_info", "police_station"], ["fir_details", "ps"]])
    district = _get_multi([["case_info", "district"], ["fir_details", "district"]])
    sections = _get_multi([["case_info", "under_sections"], "acts_and_sections"])
    date_reg = _format_date(_get_multi([["case_info", "registration_date"], ["fir_details", "date"]]))
    complainant = _get_multi([["complainant_informant", "name"]])
    complainant_addr = _get_multi([["complainant_informant", "present_address"]])
    accused_name = _get_multi([["accused_details", "name"], "name"])
    accused_parent = _get_multi([["accused_details", "relation"], "parent_name"])
    accused_age = _get_multi([["accused_details", "age"], "age"])
    accused_occ = _get_multi([["accused_details", "occupation"], "occupation"])
    accused_addr = _get_multi([["accused_details", "present_address"], "residence"])
    io_name = _get_multi([["investigating_officer", "name"], ["case_info", "investigating_officer"]])
    io_rank = _get_multi([["investigating_officer", "rank"], ["case_info", "io_rank"]])
    io_badge = _get_multi([["investigating_officer", "number"], ["case_info", "io_badge"]])
    sho_name = _get_multi([["officer_in_charge", "name"], ["case_info", "sho_name"]])
    sho_rank = _get_multi([["officer_in_charge", "rank"], ["case_info", "sho_rank"]])
    court_name = _get_multi([["case_info", "court_name"]], "[COURT NAME]")
    paragraphs = _safe_paragraphs(final_report_text)
    narrative = _summarize_narrative(paragraphs)
    medical_block = _build_medical_section(victim_medical_data, accused_medical_data)
    fir_brief = _get_multi(["brief_facts"], "The investigation was initiated based on the First Information Report.")

    # ---------- Assemble ----------
    return textwrap.dedent(f"""
    GOA POLICE
    FINAL FORM/REPORT (Under Section 173 Cr.P.C.)

    Police Station: {police_station}
    District: {district}
    Crime No: {crime_no}
    Date Registered: {date_reg}
    Sections of Law: {sections}

    ------------------ COMPLAINANT/INFORMANT ------------------
    Name: {complainant}
    Address: {complainant_addr}

    ------------------ ACCUSED DETAILS ------------------
    Name: {accused_name}
    Relation: {accused_parent}
    Age: {accused_age}
    Occupation: {accused_occ}
    Address: {accused_addr}

    ------------------ INVESTIGATION OFFICER ------------------
    Name: {io_name}
    Rank: {io_rank}
    Badge No: {io_badge}

    ------------------ STATION HOUSE OFFICER ------------------
    Name: {sho_name}
    Rank: {sho_rank}

    ------------------ BRIEF FACTS OF THE CASE ------------------
    BEFORE THE HONOURABLE COURT OF {court_name}
    MAY IT PLEASE YOUR HONOUR,

    {fir_brief}

    {narrative}

    ------------------ MEDICAL / EXPERT OPINION ------------------
    {medical_block}

    ------------------ FINAL CONCLUSION ------------------
    Based on the FIR, statements, medical evidence and investigation,
    it is submitted that the accused has committed the offences mentioned.

    Date: {now.strftime("%d/%m/%Y")}
    Place: {district}

    Investigating Officer
    Name: {io_name}
    Rank: {io_rank}
    Signature: ___________________

    Station House Officer
    Name: {sho_name}
    Rank: {sho_rank}
    Signature: ___________________
    """).strip()

# ===============================================================================
# SECTION 4: MAIN EXECUTION
# ===============================================================================

def main():
    """Main function to orchestrate the report and chargesheet generation."""
    print("🚀 Starting Nyaya AI Final Report and Chargesheet generation...")

    # 1. Read all source files
    statement_data = read_json_file(VICTIM_STATEMENT_FILE)
    victim_medical_data = read_json_file(VICTIM_MEDICAL_REPORT_FILE)
    accused_medical_data = read_json_file(ACCUSED_MEDICAL_REPORT_FILE)
    case_diary_text = read_text_file(CASE_DIARY_FILE)

    if not all([statement_data, victim_medical_data, accused_medical_data, case_diary_text]):
        print("Fatal Error: One or more essential input files could not be read. Exiting.")
        return
        
    # 2. Synthesize the Final Report for AI analysis
    final_report_for_ai = generate_final_report_for_ai(
        case_diary_text, 
        get_val(statement_data, 'narrative'),
        get_val(victim_medical_data, 'provisional_medical_opinion'),
        get_val(accused_medical_data, 'opinion')
    )

    # 3. Generate the final Chargesheet using all relevant data
    chargesheet_content = generate_chargesheet(
        final_report_for_ai, 
        statement_data, 
        accused_medical_data, 
        victim_medical_data,
        FIR_FILE
    )

    # 4. Write all generated files to disk
    with open(FINAL_REPORT_FILE, 'w', encoding='utf-8') as f: f.write(final_report_for_ai)
    with open(CHARGESHEET_FILE, 'w', encoding='utf-8') as f: f.write(chargesheet_content)

    print("\n✅ Pipeline finished successfully. Output files have been generated:")
    print(f"- Final Report (AI):    {FINAL_REPORT_FILE}")
    print(f"- Chargesheet Draft:    {CHARGESHEET_FILE}")

if __name__ == "__main__":
    main()