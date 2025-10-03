# ==============================================================================
# NYAYA AI - SOP COMPLIANCE CHECKLIST GENERATOR
# ===============================================================================
# This script reads all relevant case files (FIR, Statement, Medical Reports)
# and compares them against a list of Standard Operating Procedures (SOP) to
# generate an interactive compliance checklist in Markdown format.
# ===============================================================================

import json
import os
import re
from typing import List, Dict, Any, Optional

# ===============================================================================
# SECTION 1: CONFIGURATION - FILE PATHS
# ===============================================================================

# --- INPUT FILES ---
# NOTE: Update these paths to match your local file structure.
DATA_DIR = "json_generator\\output"
FIR_FILE = os.path.join(DATA_DIR, "FIR.json")
VICTIM_STATEMENT_FILE = os.path.join(DATA_DIR, "statement.json")
VICTIM_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "victim_med_rep.json")
ACCUSED_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "accused_med_rep.json")
SOP_FILE = os.path.join(DATA_DIR, "rules_output.json")

# --- OUTPUT FILE ---
CHECKLIST_FILE = "Report_generator\\Outputs\\compliance_checklist.md"


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

def has_meaningful_data(data: Optional[Dict[str, Any]]) -> bool:
    """Checks if a dictionary is not None and contains at least one non-empty value."""
    if not data or not isinstance(data, dict):
        return False
    for value in data.values():
        if value is not None:
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, (list, dict)) and value:
                return True
            if isinstance(value, (int, float, bool)):
                return True
    return False
    
def get_val(data: Dict[str, Any], key: str, default: Any = '[N/A]') -> Any:
    """Safely gets a value from a dictionary."""
    if not isinstance(data, dict): return default
    val = data.get(key)
    return default if val is None or (isinstance(val, (str, list, dict)) and not val) else val

def get_nested_val(data: Dict[str, Any], path: List[str], default: Any = '[N/A]') -> Any:
    """Safely gets a value from a nested dictionary."""
    if not isinstance(data, dict): return default
    current_level = data
    for key in path:
        if not isinstance(current_level, dict) or key not in current_level: return default
        current_level = current_level.get(key)
    return default if current_level is None or (isinstance(current_level, (str, list, dict)) and not current_level) else current_level

def get_victim_age(statement_data: Dict[str, Any], medical_data: Dict[str, Any]) -> Optional[int]:
    """Extracts the victim's age from various fields in the report files."""
    # Prioritize medical report age
    age_str = str(get_val(medical_data, 'age', default='')).replace('years', '').strip()
    if age_str.isdigit():
        return int(age_str)
    
    # Fallback to statement age
    age_str = str(get_nested_val(statement_data, ['witness_details', 'age'], default='')).replace('years', '').strip()
    if age_str.isdigit():
        return int(age_str)
        
    # Fallback to narrative search
    narrative = get_val(statement_data, 'narrative', default=None)
    if narrative:
        match = re.search(r'age[\s:]*(\d+)', narrative, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

# ===============================================================================
# SECTION 3: COMPLIANCE CHECK LOGIC
# ===============================================================================

def check_sop_compliance(
    fir_data: Dict, 
    statement_data: Dict, 
    victim_medical_data: Dict, 
    accused_medical_data: Dict, 
    sop_rules: List[Dict], 
    is_minor: Optional[bool]
) -> tuple:
    """Checks SOP rules and categorizes them based on completion and POCSO applicability."""
    pocso_completed, pocso_incomplete = [], []
    general_completed, general_incomplete = [], []

    for rule in sop_rules:
        procedure = rule.get("procedure", "N/A").lower()
        details = rule.get("details", "N/A").lower()
        is_pocso_rule = 'pocso' in details or 'pocso' in procedure

        # Skip POCSO-specific rules if the victim is confirmed to be an adult
        if is_minor is False and is_pocso_rule:
            continue

        is_complete = False
        # Updated logic to check all specified input files
        if "fir" in procedure:
            is_complete = has_meaningful_data(fir_data)
        elif "statement of victim" in procedure:
            is_complete = has_meaningful_data(statement_data)
        elif "medical examination of victim" in procedure:
            is_complete = has_meaningful_data(victim_medical_data)
        elif "medical examination" in procedure and "accused" in details:
            is_complete = has_meaningful_data(accused_medical_data)
        
        rule_text = f"- {rule.get('procedure', 'N/A')}: {rule.get('details', 'N/A')}"
        
        if is_pocso_rule:
            (pocso_completed if is_complete else pocso_incomplete).append(rule_text)
        else:
            (general_completed if is_complete else general_incomplete).append(rule_text)

    return pocso_completed, pocso_incomplete, general_completed, general_incomplete

def generate_checklist_md(pocso_completed: List, pocso_incomplete: List, general_completed: List, general_incomplete: List, is_minor: Optional[bool]) -> str:
    """Generates an interactive Markdown checklist file from sorted rule lists."""
    checklist = "# SOP Compliance Checklist\n\n"
    
    if is_minor is None:
        checklist += "## ⚠️ Case Status: VICTIM'S AGE UNKNOWN\n> **Note:** All procedures are displayed until age is confirmed.\n\n"
    elif is_minor:
        checklist += "## ⚖️ VICTIM IS A MINOR\n> **Note:** POCSO Act procedures are prioritized.\n\n"
    else:
        checklist += "## ✅ Victim is NOT a minor\n> **Note:** POCSO-related procedures are hidden.\n\n"

    def format_steps(steps: List[str], is_done: bool) -> str:
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

# ===============================================================================
# SECTION 4: MAIN EXECUTION
# ===============================================================================

def main():
    """Main function to orchestrate the checklist generation."""
    print("🚀 Starting Nyaya AI SOP Compliance Checklist generation...")

    # 1. Read all source files
    fir_data = read_json_file(FIR_FILE)
    statement_data = read_json_file(VICTIM_STATEMENT_FILE)
    victim_medical_data = read_json_file(VICTIM_MEDICAL_REPORT_FILE)
    accused_medical_data = read_json_file(ACCUSED_MEDICAL_REPORT_FILE)
    sop_rules = read_json_file(SOP_FILE)

    if not sop_rules:
        print("Fatal Error: SOP rules file (`rules_output.json`) could not be read. Exiting.")
        return

    # 2. Analyze data to determine case type (POCSO vs. General)
    victim_age = get_victim_age(statement_data or {}, victim_medical_data or {})
    is_minor = victim_age < 18 if victim_age is not None else None

    # 3. Perform the compliance check
    pocso_completed, pocso_incomplete, general_completed, general_incomplete = check_sop_compliance(
        fir_data, statement_data, victim_medical_data, accused_medical_data, sop_rules, is_minor
    )
    
    # 4. Generate the final Markdown content
    checklist_md_content = generate_checklist_md(
        pocso_completed, pocso_incomplete, general_completed, general_incomplete, is_minor
    )
    
    # 5. Write the checklist to disk
    with open(CHECKLIST_FILE, 'w', encoding='utf-8') as f:
        f.write(checklist_md_content)

    print("\n✅ Compliance Checklist generation finished successfully.")
    print(f"- Output file: {CHECKLIST_FILE}")

if __name__ == "__main__":
    main()