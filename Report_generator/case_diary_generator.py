import json
import os
import datetime
from typing import List, Dict, Any, Optional

# ===============================================================================
# SECTION 1: CONFIGURATION - FILE PATHS
# ===============================================================================

# --- INPUT FILES ---
# NOTE: Update these paths to match your local file structure.
DATA_DIR = "json_generator\\output"
VICTIM_STATEMENT_FILE = os.path.join(DATA_DIR, "statement.json")
VICTIM_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "victim_med_rep.json")
ACCUSED_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "accused_med_rep.json")
# Added FIR file as an input source
FIR_FILE = os.path.join(DATA_DIR, "FIR.json")


# --- OUTPUT FILE ---
CASE_DIARY_FILE = "Report_generator\\Outputs\\case_diary.txt"

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

def get_val(data: Dict[str, Any], key: str, default: Any = '[N/A]') -> Any:
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

# ===============================================================================
# SECTION 3: CASE DIARY GENERATION (MODIFIED)
# ===============================================================================

def generate_case_diary(
    fir_data: Dict[str, Any], 
    statement_data: Dict[str, Any], 
    victim_medical_data: Dict[str, Any], 
    accused_medical_data: Dict[str, Any]
) -> str:
    """Generates a detailed case diary text file using FIR as the primary source for case info."""
    
    # Use FIR data as the primary source for case info
    fir_details = get_val(fir_data, 'fir_details', {})
    
    diary = f"CASE DIARY\n\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    diary += f"Police Station: {get_val(fir_details, 'ps')}\n"
    diary += f"Crime No: {get_val(fir_details, 'fir_no')}\n"
    diary += "--------------------------------------\n\n"

    diary += "1. Complainant/Informant Details (from FIR):\n"
    diary += f"   Name: {get_nested_val(fir_data, ['complainant_informant', 'name'])}\n"
    diary += f"   Address: {get_nested_val(fir_data, ['complainant_informant', 'present_address'])}\n\n"

    diary += "2. Accused Details (from FIR):\n"
    diary += f"   Name: {get_nested_val(fir_data, ['accused_details', 'name'])}\n"
    diary += f"   Address: {get_nested_val(fir_data, ['accused_details', 'present_address'])}\n\n"

    diary += f"3. Brief Facts (from FIR):\n   {get_val(fir_data, 'brief_facts')}\n\n"
    
    diary += f"4. Victim's Statement Summary:\n   {get_val(statement_data, 'narrative')}\n\n"
    
    diary += f"5. Medical Examination Summary (Victim):\n   Provisional Opinion: {get_val(victim_medical_data, 'provisional_medical_opinion')}\n\n"
    
    diary += f"6. Medical Examination Summary (Accused):\n   Provisional Opinion: {get_val(accused_medical_data, 'opinion')}\n\n"
    
    return diary

# ===============================================================================
# SECTION 4: MAIN EXECUTION (MODIFIED)
# ===============================================================================

def main():
    """Main function to orchestrate the case diary generation."""
    print("🚀 Starting Nyaya AI Case Diary generation...")

    # 1. Read all source files
    fir_data = read_json_file(FIR_FILE)
    statement_data = read_json_file(VICTIM_STATEMENT_FILE)
    victim_medical_data = read_json_file(VICTIM_MEDICAL_REPORT_FILE)
    accused_medical_data = read_json_file(ACCUSED_MEDICAL_REPORT_FILE)

    if not all([fir_data, statement_data, victim_medical_data, accused_medical_data]):
        print("Fatal Error: One or more essential JSON files (FIR, statement, medical reports) could not be read. Exiting.")
        return

    # 2. Generate the case diary
    case_diary_content = generate_case_diary(fir_data, statement_data, victim_medical_data, accused_medical_data)
    
    # 3. Write the case diary to disk
    with open(CASE_DIARY_FILE, 'w', encoding='utf-8') as f:
        f.write(case_diary_content)

    print("\n✅ Case Diary generation finished successfully.")
    print(f"- Output file: {CASE_DIARY_FILE}")

if __name__ == "__main__":
    main()