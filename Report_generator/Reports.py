# ==============================================================================
# NYAYA AI - UNIFIED PROCESSING SCRIPT (Corrected)
# ===============================================================================
# This script performs the entire pipeline:
# 1. Reads and parses raw case files (FIR, Medical, Statement, SOP).
# 2. Performs SOP compliance checks and generates an interactive checklist.
# 3. Generates a detailed Case Diary.
# 4. Synthesizes a comprehensive Final Report for AI analysis.
# 5. Uses the case files and AI-summary to generate an accurate, auto-filled Chargesheet.
#
# Installation requirements:
# pip install numpy faiss-cpu sentence-transformers
# ===============================================================================

import json
import os
import re
import datetime
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

# ===============================================================================
# SECTION 1: CONFIGURATION - FILE PATHS
# ===============================================================================

# --- INPUT FILES ---
# NOTE: Update these paths to match your local file structure.
DATA_DIR = "D:\\Goa_p_hackathon\\Team_Sisyphus\\json_generator\\output" # Assuming files are in the same directory as the script
# The script relies on JSON outputs from the parsers. We use statement and medical reports as primary sources.
# The original FIR_FILE is commented out as it can be an unreliable source.
# FIR_FILE = os.path.join(DATA_DIR, "fir.json")
VICTIM_STATEMENT_FILE = os.path.join(DATA_DIR, "statement.json")
VICTIM_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "victim_med_rep.json")
ACCUSED_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "accused_med_rep.json")
SOP_FILE = os.path.join(DATA_DIR, "rules_output.json")

# --- OUTPUT FILES ---
CHECKLIST_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\compliance_checklist.md"
CASE_DIARY_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\case_diary.txt"
FINAL_REPORT_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\final_report.txt"
CHARGESHEET_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\chargesheet.md"


# ===============================================================================
# SECTION 2: UTILITY FUNCTIONS (UPDATED)
# ===============================================================================

def read_json_file(file_path):
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

def get_nested_val(data: Dict[str, Any], path: List[str], default: Any = '[N/A]') -> Any:
    """Safely gets a value from a nested dictionary using a list of keys."""
    if not isinstance(data, dict):
        return default
    current_level = data
    for key in path:
        if not isinstance(current_level, dict) or key not in current_level:
            return default
        current_level = current_level.get(key)
    
    if current_level is None or (isinstance(current_level, (str, list, dict)) and not current_level):
        return default
    return current_level

def get_val(data, key, default='[N/A]'):
    """
    Safely gets a value from a dictionary.
    Returns the default value if the dictionary is None, the key doesn't exist,
    or the value associated with the key is None or an empty string/list/dict.
    """
    if not isinstance(data, dict):
        return '[Data unavailable]'
    
    val = data.get(key)
    
    if val is None or (isinstance(val, (str, list, dict)) and not val):
        return default
    return val

def has_meaningful_data(data):
    """Checks if a dictionary contains at least one non-null/non-empty value."""
    if not data or not isinstance(data, dict):
        return False
    for value in data.values():
        if value is not None:
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, (list, dict)) and not value:
                continue
            return True
    return False

def get_victim_age(statement_data, medical_data):
    """Extracts the victim's age from various fields in the report files."""
    # Prioritize medical report age
    age_str = get_val(medical_data, 'age', default='').replace('years', '').strip()
    if age_str.isdigit():
        return int(age_str)
    
    # Fallback to statement age
    age_str = get_nested_val(statement_data, ['witness_details', 'age'], default='').replace('years', '').strip()
    if age_str.isdigit():
        return int(age_str)
        
    # Fallback to narrative search
    narrative = get_val(statement_data, 'narrative', default=None)
    if narrative:
        match = re.search(r'Age:\s*(\d+)', narrative, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

# ===============================================================================
# SECTION 3: REPORT GENERATION (COMPLIANCE, DIARY, FINAL REPORT)
# ===============================================================================

# This section remains unchanged as its logic is sound.
def check_sop_compliance(statement_data, victim_medical_data, accused_medical_data, sop_rules, is_minor):
    """Checks SOP rules and categorizes them into POCSO/General and Completed/Incomplete."""
    pocso_completed, pocso_incomplete = [], []
    general_completed, general_incomplete = [], []

    for rule in sop_rules:
        procedure = rule.get("procedure", "N/A")
        details = rule.get("details", "N/A")
        is_pocso_rule = 'pocso' in details.lower() or 'pocso' in procedure.lower()

        if is_minor is False and is_pocso_rule:
            continue

        is_complete = False
        if "medical examination of victim" in procedure.lower():
            is_complete = has_meaningful_data(victim_medical_data)
        elif "medical examination" in procedure.lower() and "accused" in details.lower():
            is_complete = has_meaningful_data(accused_medical_data)
        elif "statement of victim" in procedure.lower():
            is_complete = has_meaningful_data(statement_data)
        # Assuming FIR is always filed if a statement exists
        elif "fir" in procedure.lower():
            is_complete = has_meaningful_data(statement_data) 
        
        rule_text = f"- {procedure}: {details}"
        
        target_list = (pocso_completed if is_complete else pocso_incomplete) if is_pocso_rule else (general_completed if is_complete else general_incomplete)
        target_list.append(rule_text)

    return pocso_completed, pocso_incomplete, general_completed, general_incomplete

def generate_checklist_md(pocso_completed, pocso_incomplete, general_completed, general_incomplete, is_minor):
    """Generates an interactive Markdown checklist file."""
    checklist = "# SOP Compliance Checklist\n\n"
    
    if is_minor is None:
        checklist += "## ⚠️ Case Status: VICTIM'S AGE UNKNOWN\n> **Note:** All procedures are displayed until age is confirmed.\n\n"
    elif is_minor:
        checklist += "## ⚖️ VICTIM IS A MINOR\n> **Note:** POCSO Act procedures are prioritized.\n\n"
    else:
        checklist += "## Victim is NOT a minor\n> **Note:** POCSO-related procedures are hidden.\n\n"

    def format_steps(steps, is_done):
        marker = "[x]" if is_done else "[ ]"
        return "\n".join(step.replace("- ", f"- {marker} ", 1) for step in steps) + "\n" if steps else ""

    if is_minor is not False:
        checklist += "### POCSO Act Procedures (Priority)\n"
        if pocso_incomplete: checklist += "#### 🚨 To-Do\n" + format_steps(pocso_incomplete, False)
        if pocso_completed: checklist += "#### ✅ Completed\n" + format_steps(pocso_completed, True)
    
    checklist += "### General Procedures\n"
    if general_incomplete: checklist += "#### 🚨 To-Do\n" + format_steps(general_incomplete, False)
    if general_completed: checklist += "#### ✅ Completed\n" + format_steps(general_completed, True)
    
    return checklist

def generate_case_diary(statement_data, victim_medical_data, accused_medical_data):
    """Generates a detailed case diary text file."""
    # Use statement data as the primary source for case info
    case_info = get_val(statement_data, 'case_info', {})
    diary = f"CASE DIARY\n\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    diary += f"Police Station: {get_val(case_info, 'police_station')}\n"
    diary += f"Crime No: {get_val(case_info, 'crime_no')}\n"
    diary += "--------------------------------------\n\n"

    diary += "1. Complainant/Informant Details:\n"
    # Victim's statement is the complainant
    witness_details = get_val(statement_data, 'witness_details', {})
    diary += f"   Name: {get_nested_val(statement_data, ['witness_details', 'name'])}\n   Address: {get_nested_val(statement_data, ['witness_details', 'address'])}\n\n"

    diary += "2. Accused Details:\n"
    diary += f"   Name: {get_val(accused_medical_data, 'name')}\n   Address: {get_val(accused_medical_data, 'residence')}\n\n"

    diary += f"3. Brief Facts from Victim Statement:\n   {get_val(statement_data, 'narrative')}\n\n"
    diary += f"4. Victim's Statement Summary:\n   {get_val(statement_data, 'narrative')}\n\n"
    diary += f"5. Medical Examination Summary (Victim):\n   Provisional Opinion: {get_val(victim_medical_data, 'provisional_medical_opinion')}\n\n"
    diary += f"6. Medical Examination Summary (Accused):\n   Provisional Opinion: {get_val(accused_medical_data, 'opinion')}\n\n"
    return diary

def generate_final_report_for_ai(case_diary, statement_narrative, victim_medical_opinion, accused_medical_opinion):
    """Synthesizes a text report from key sources, optimized for AI analysis."""
    report = "FINAL INVESTIGATION REPORT (AI FEED)\n\n"
    report += "This document synthesizes information from the case diary, victim's full statement, and medical reports to provide a comprehensive narrative for analysis.\n"
    report += "==================================================================\n\n"
    report += "I. NARRATIVE FROM CASE DIARY\n--------------------------\n"
    report += case_diary + "\n\n"
    report += "II. FULL VICTIM STATEMENT\n--------------------------\n"
    report += statement_narrative + "\n\n"
    report += "III. MEDICAL OPINIONS\n--------------------------\n"
    report += f"Victim Medical Opinion: {victim_medical_opinion}\n"
    report += f"Accused Medical Opinion: {accused_medical_opinion}\n\n"
    report += "==================================================================\nEnd of Report\n"
    return report

# ===============================================================================
# SECTION 4: AI AND CHARGESHEET GENERATION (REVISED)
# ===============================================================================

def get_embeddings(text_list: list[str], model) -> np.ndarray:
    """Encodes a list of text into vector embeddings."""
    return model.encode(text_list, convert_to_tensor=False)

import datetime
import re
import textwrap

# Optional ML imports. Code degrades gracefully if unavailable.
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False

import datetime
import re
import textwrap

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False


import datetime
import re
import textwrap
import json
import os

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False


def generate_chargesheet(final_report_text: str,
                         statement_data: dict,
                         accused_medical_data: dict,
                         victim_medical_data: dict,
                         fir_path: str = "D:\\Goa_p_hackathon\\Team_Sisyphus\\json_generator\\output\\fir.json",
                         additional_data: dict = None) -> str:
    """
    Generate a FORM IF5 style chargesheet.
    Data priority: statement_data > medical_data > FIR JSON > additional_data
    """

    # Load FIR JSON if file exists
    fir_data = {}
    if fir_path and os.path.exists(fir_path):
        with open(fir_path, "r", encoding="utf-8") as f:
            fir_data = json.load(f)

    additional_data = additional_data or {}

    # ---------- Helpers ----------
    def _get_nested(d, keys, default="[N/A]"):
        cur = d
        for k in keys:
            if not isinstance(cur, dict):
                return default
            cur = cur.get(k, default)
        return cur if cur not in (None, "", [], {}) else default

    def _get_multi(paths, default="[N/A]"):
        """Try multiple key paths across all sources"""
        if not isinstance(paths, list):
            paths = [paths]
        sources = [statement_data, victim_medical_data, accused_medical_data, fir_data, additional_data]
        for path in paths:
            for src in sources:
                val = _get_nested(src, path if isinstance(path, list) else [path], default=None)
                if val not in (None, "", [], {}):
                    return val
        return default

    def _format_date(val, fmt="%d/%m/%Y"):
        if not val or val in ("[N/A]", None):
            return "[N/A]"
        if isinstance(val, (datetime.date, datetime.datetime)):
            return val.strftime(fmt)
        # Convert DD-MM-YYYY etc.
        for pat in (r"(\d{2})[-/.](\d{2})[-/.](\d{4})",):
            m = re.match(pat, str(val))
            if m:
                d, mth, y = m.groups()
                return f"{d}/{mth}/{y}"
        return str(val)

    def _safe_paragraphs(text):
        if not text:
            return []
        return [p.strip() for p in re.split(r'\n+', text) if p.strip() and len(p.strip()) > 20]

    def _summarize_narrative(paragraphs, top_k=3):
        if not paragraphs:
            return "[Narrative missing]"
        if ML_AVAILABLE:
            try:
                model = SentenceTransformer("ai4bharat/indic-bert")
                emb_par = np.array(model.encode(paragraphs, show_progress_bar=False))
                emb_q = np.array(model.encode([
                    "initial complaint sequence of events",
                    "victim account",
                    "medical findings",
                    "how accused identified"
                ], show_progress_bar=False))
                dim = emb_par.shape[1]
                index = faiss.IndexFlatL2(dim)
                index.add(emb_par.astype("float32"))
                _, I = index.search(emb_q.astype("float32"), k=min(2, len(paragraphs)))
                picked = [paragraphs[idx] for row in I for idx in row if idx >= 0]
                return "\n\n".join(dict.fromkeys(picked)) or paragraphs[0]
            except Exception:
                pass
        return "\n\n".join(paragraphs[:top_k])

    def _format_dict_as_bullets(data: dict, keys: list) -> str:
        lines = []
        for k in keys:
            val = _get_nested(data, [k], None)
            if val:
                lines.append(f"- {k.replace('_',' ').title()}: {val}")
        return "\n".join(lines) if lines else "[N/A]"

    def _build_medical_section(victim_md, accused_md):
        victim_keys = ["name", "age", "address",
                       "history_of_violence", "genital_examination_findings",
                       "provisional_medical_opinion"]
        accused_keys = ["name", "age", "opinion", "findings"]

        victim_block = _format_dict_as_bullets(victim_md, victim_keys)
        accused_block = _format_dict_as_bullets(accused_md, accused_keys)

        return (
            "Victim Medical/Expert Opinion:\n" + textwrap.indent(victim_block, "  ") + "\n\n"
            "Accused Medical/Expert Opinion:\n" + textwrap.indent(accused_block, "  ")
        )

    # ---------- Pull Data ----------
    now = datetime.datetime.now()
    crime_no       = _get_multi([["case_info","crime_no"], ["fir_details","fir_no"]])
    police_station = _get_multi([["case_info","police_station"], ["fir_details","ps"]])
    district       = _get_multi([["case_info","district"], ["fir_details","district"]])
    sections       = _get_multi([["case_info","under_sections"], "acts_and_sections"])
    date_reg       = _format_date(_get_multi([["case_info","registration_date"], ["fir_details","date"]]))

    complainant    = _get_multi([["complainant_informant","name"]])
    complainant_addr = _get_multi([["complainant_informant","present_address"]])

    accused_name   = _get_multi([["accused_details","name"], "name"])
    accused_parent = _get_multi([["accused_details","relation"], "parent_name"])
    accused_age    = _get_multi([["accused_details","age"], "age"])
    accused_occ    = _get_multi([["accused_details","occupation"], "occupation"])
    accused_addr   = _get_multi([["accused_details","present_address"], "residence"])

    io_name        = _get_multi([["investigating_officer","name"], ["case_info","investigating_officer"]])
    io_rank        = _get_multi([["investigating_officer","rank"], ["case_info","io_rank"]])
    io_badge       = _get_multi([["investigating_officer","number"], ["case_info","io_badge"]])

    sho_name       = _get_multi([["officer_in_charge","name"], ["case_info","sho_name"]])
    sho_rank       = _get_multi([["officer_in_charge","rank"], ["case_info","sho_rank"]])

    court_name     = _get_multi([["case_info","court_name"]], "[COURT NAME]")

    paragraphs     = _safe_paragraphs(final_report_text)
    narrative      = _summarize_narrative(paragraphs)
    medical_block  = _build_medical_section(victim_medical_data, accused_medical_data)

    fir_brief      = _get_multi(["brief_facts"], "")

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
# SECTION 5: MAIN EXECUTION (REVISED)
# ===============================================================================

def main():
    """Main function to orchestrate the entire script."""
    print("🚀 Starting Nyaya AI case processing pipeline...")

    # 1. Read all source files
    statement_data = read_json_file(VICTIM_STATEMENT_FILE)
    victim_medical_data = read_json_file(VICTIM_MEDICAL_REPORT_FILE)
    accused_medical_data = read_json_file(ACCUSED_MEDICAL_REPORT_FILE)
    sop_rules = read_json_file(SOP_FILE)

    if not sop_rules or not statement_data or not victim_medical_data or not accused_medical_data:
        print("Fatal Error: One or more essential JSON files (statement, medical reports, SOP) could not be read. Exiting.")
        return

    # 2. Analyze data and generate initial reports
    victim_age = get_victim_age(statement_data, victim_medical_data)
    is_minor = victim_age < 18 if victim_age is not None else None

    pocso_completed, pocso_incomplete, general_completed, general_incomplete = check_sop_compliance(
        statement_data, victim_medical_data, accused_medical_data, sop_rules, is_minor
    )
    
    checklist_md = generate_checklist_md(pocso_completed, pocso_incomplete, general_completed, general_incomplete, is_minor)
    case_diary = generate_case_diary(statement_data, victim_medical_data, accused_medical_data)
    
    # 3. Synthesize the Final Report for AI analysis
    final_report_for_ai = generate_final_report_for_ai(
        case_diary, 
        get_val(statement_data, 'narrative'),
        get_val(victim_medical_data, 'provisional_medical_opinion'),
        get_val(accused_medical_data, 'opinion')
    )

    # 4. Generate the final Chargesheet using all relevant data
    chargesheet_content = generate_chargesheet(
        final_report_for_ai, 
        statement_data, 
        accused_medical_data, 
        victim_medical_data
    )

    # 5. Write all generated files to disk
    with open(CHECKLIST_FILE, 'w', encoding='utf-8') as f: f.write(checklist_md)
    with open(CASE_DIARY_FILE, 'w', encoding='utf-8') as f: f.write(case_diary)
    with open(FINAL_REPORT_FILE, 'w', encoding='utf-8') as f: f.write(final_report_for_ai)
    with open(CHARGESHEET_FILE, 'w', encoding='utf-8') as f: f.write(chargesheet_content)

    print("\n✅ Pipeline finished successfully. Output files have been generated:")
    print(f"- Compliance Checklist: {CHECKLIST_FILE}")
    print(f"- Case Diary:           {CASE_DIARY_FILE}")
    print(f"- Final Report (AI):    {FINAL_REPORT_FILE}")
    print(f"- Chargesheet Draft:    {CHARGESHEET_FILE}")

if __name__ == "__main__":
    main()