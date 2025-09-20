import json
import os
import re
from datetime import datetime

# Define file paths for clarity
DATA_DIR = "D:\\Goa_p_hackathon\\Team_Sisyphus\\json_generator\\output"
FIR_FILE = os.path.join(DATA_DIR, "FIR.json")
VICTIM_STATEMENT_FILE = os.path.join(DATA_DIR, "statement compressed.json")
VICTIM_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "victim report to PDF 20250907 12.57.07-compressed.json")
ACCUSED_MEDICAL_REPORT_FILE = os.path.join(DATA_DIR, "Accuse medical examination to PDF 20250907 13.02.08.json")
SOP_FILE = os.path.join(DATA_DIR, "rules_output.json")

# Output files
CHECKLIST_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\compliance_checklist.md"
CASE_DIARY_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\case_diary.txt"
FINAL_REPORT_FILE = "D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\final_report.txt"

def read_json_file(file_path):
    """Reads and parses a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Check if file is empty
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

def has_meaningful_data(data):
    """
    Checks if a dictionary loaded from JSON contains at least one non-null/non-empty value.
    Returns False if data is None, an empty dict, or all values are None/empty strings/empty collections.
    """
    if not data or not isinstance(data, dict):
        return False
    # Check if any value in the dictionary has content.
    for value in data.values():
        if value is not None:
            # Check for empty strings, lists, or dicts
            if isinstance(value, str) and not value.strip():
                continue  # It's an empty or whitespace-only string
            if isinstance(value, (list, dict)) and not value:
                continue  # It's an empty list or dict
            return True  # Found a meaningful value
    return False

def get_victim_age(statement_data, medical_data):
    """Extracts the victim's age from report files."""
    # First, try to get age from a dedicated field in the medical report
    if medical_data and isinstance(medical_data.get('age'), int):
        return medical_data.get('age')
    
    # Second, try a dedicated field in the statement
    if statement_data and isinstance(statement_data.get('witness_details', {}).get('age'), int):
        return statement_data.get('witness_details', {}).get('age')

    # Finally, try to parse the age from the narrative text in the statement
    if statement_data and statement_data.get('narrative'):
        narrative = statement_data.get('narrative')
        match = re.search(r'Age:\s*(\d+)', narrative, re.IGNORECASE)
        if match:
            return int(match.group(1))
            
    return None

def check_sop_compliance(fir_data, statement_data, victim_medical_data, accused_medical_data, sop_rules, is_minor):
    """Separates rules into POCSO/General and checks compliance."""
    pocso_completed, pocso_incomplete = [], []
    general_completed, general_incomplete = [], []

    for rule in sop_rules:
        procedure = rule.get("procedure", "N/A")
        details = rule.get("details", "N/A")
        procedure_lower = procedure.lower()
        details_lower = details.lower()
        
        is_pocso_rule = 'pocso' in details_lower or 'pocso' in procedure_lower
        
        # If the victim is confirmed NOT a minor, skip POCSO rules.
        if is_minor is False and is_pocso_rule:
            continue

        is_complete = False
        if "medical examination of victim" in procedure_lower:
            is_complete = has_meaningful_data(victim_medical_data)
        elif "medical examination" in procedure_lower and "accused" in details_lower:
            is_complete = has_meaningful_data(accused_medical_data)
        elif "statement of victim" in procedure_lower:
            is_complete = has_meaningful_data(statement_data)
        elif "fir" in procedure_lower:
            is_complete = has_meaningful_data(fir_data)
        elif "charge sheet" in procedure_lower:
            is_complete = False

        rule_text = f"- {procedure}: {details}"
        
        if is_pocso_rule:
            if is_complete:
                pocso_completed.append(rule_text)
            else:
                pocso_incomplete.append(rule_text)
        else:
            if is_complete:
                general_completed.append(rule_text)
            else:
                general_incomplete.append(rule_text)

    return pocso_completed, pocso_incomplete, general_completed, general_incomplete

def generate_case_diary(fir_data, statement_data, victim_medical_data, accused_medical_data):
    """Generates a case diary from the available data, noting missing files."""
    diary = "CASE DIARY\n\n"
    now = datetime.now()
    diary += f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    police_station = fir_data.get('police_station', 'N/A') if fir_data else "[Data unavailable: FIR.json not found or empty]"
    fir_no = fir_data.get('fir_no', 'N/A') if fir_data else "[Data unavailable: FIR.json not found or empty]"
    diary += f"Police Station: {police_station}\n"
    diary += f"FIR No: {fir_no}\n"
    diary += "--------------------------------------\n\n"

    diary += "1. Complainant/Informant Details:\n"
    if fir_data:
        complainant = fir_data.get('complainant_informant', {})
        diary += f"   Name: {complainant.get('name', 'N/A')}\n"
        diary += f"   Address: {complainant.get('address', 'N/A')}\n\n"
    else:
        diary += "   [Data unavailable: FIR.json not found or empty]\n\n"

    diary += "2. Accused Details:\n"
    if fir_data and fir_data.get('accused_details'):
        for i, accused in enumerate(fir_data.get('accused_details', [])):
            diary += f"   Accused {i+1}:\n"
            diary += f"     Name: {accused.get('name', 'N/A')}\n"
            diary += f"     Address: {accused.get('address', 'N/A')}\n"
    else:
        diary += "   [Data unavailable: FIR.json not found or empty]\n"
    diary += "\n"

    diary += "3. Brief Facts from FIR:\n"
    brief_facts = fir_data.get('brief_facts', 'No brief facts available.') if fir_data else "[Data unavailable: FIR.json not found or empty]"
    diary += f"   {brief_facts}\n\n"

    diary += "4. Victim's Statement Summary:\n"
    narrative = statement_data.get('narrative', 'No narrative available.') if statement_data else "[Data unavailable: statement compressed.json not found or empty]"
    diary += f"   {narrative}\n\n"

    diary += "5. Medical Examination Summary (Victim):\n"
    opinion = victim_medical_data.get('provisional_medical_opinion', 'No opinion available.') if victim_medical_data else "[Data unavailable: victim report JSON not found or empty]"
    diary += f"   Provisional Opinion: {opinion}\n\n"

    diary += "6. Medical Examination Summary (Accused):\n"
    opinion_accused = accused_medical_data.get('provisional_medical_opinion', 'No opinion available.') if accused_medical_data else "[Data unavailable: Accuse medical examination JSON not found or empty]"
    diary += f"   Provisional Opinion: {opinion_accused}\n\n"

    return diary

def generate_checklist_md(pocso_completed, pocso_incomplete, general_completed, general_incomplete, is_minor):
    """Generates a Markdown checklist with separate sections for POCSO rules if applicable."""
    checklist = "# SOP Compliance Checklist\n\n"

    # Helper to format a list of steps into checklist items
    def format_steps(steps, is_done):
        marker = "[x]" if is_done else "[ ]"
        return "\n".join(step.replace("- ", f"- {marker} ", 1) for step in steps) + "\n" if steps else ""

    # Add the main status header
    if is_minor is None:
        checklist += "## ⚠️ Case Status: VICTIM'S AGE UNKNOWN\n\n"
        checklist += "> **Note:** All general and POCSO-related procedures are displayed until age is confirmed.\n\n"
    elif is_minor:
        checklist += "##  याşında নাবালক (VICTIM IS A MINOR)\n\n"
    else:
        checklist += "##  yaşında প্রাপ্তবয়স্ক (Victim is NOT a minor)\n\n"
        checklist += "> **Note:** This checklist has been automatically filtered to hide POCSO-related procedures.\n\n"

    # If minor or age unknown, create the POCSO section first
    if is_minor is not False:
        checklist += "## ⚖️ POCSO Act Procedures (Priority)\n\n"
        if pocso_incomplete:
            checklist += "### 🚨 Incomplete POCSO Steps (To-Do)\n"
            checklist += format_steps(pocso_incomplete, is_done=False)
        if pocso_completed:
            checklist += "### ✅ Completed POCSO Steps\n"
            checklist += format_steps(pocso_completed, is_done=True)
        checklist += "\n"

    # General Procedures section
    checklist += "## 📋 General Procedures\n\n"
    if general_incomplete:
        checklist += "### 🚨 Incomplete General Steps (To-Do)\n"
        checklist += format_steps(general_incomplete, is_done=False)
    if general_completed:
        checklist += "### ✅ Completed General Steps\n"
        checklist += format_steps(general_completed, is_done=True)

    return checklist

def generate_final_report(pocso_completed, pocso_incomplete, general_completed, general_incomplete, case_diary, is_minor):
    """Generates a final compiled report with separate compliance sections."""
    report = "FINAL INVESTIGATION REPORT\n\n"
    report += "This report compiles and analyzes case information against the Standard Operating Procedures (SOP).\n"
    report += "------------------------------------------------------------------\n\n"
    report += "1. SOP Compliance Analysis:\n\n"

    # If minor or age unknown, create a POCSO section
    if is_minor is not False:
        report += "--- POCSO Act Procedures ---\n"
        report += "Incomplete:\n" + ("\n".join(pocso_incomplete) if pocso_incomplete else "All POCSO steps are marked as complete.")
        report += "\n\nCompleted:\n" + ("\n".join(pocso_completed) if pocso_completed else "No POCSO steps are marked as complete.")
        report += "\n\n"

    # General Procedures section
    report += "--- General Procedures ---\n"
    report += "Incomplete:\n" + ("\n".join(general_incomplete) if general_incomplete else "All general steps are marked as complete.")
    report += "\n\nCompleted:\n" + ("\n".join(general_completed) if general_completed else "No general steps are marked as complete.")
    report += "\n\n"
    
    report += "2. Case Diary:\n\n"
    report += case_diary

    report += "\n------------------------------------------------------------------\n"
    report += "End of Report\n"
    return report

def main():
    """Main function to orchestrate the script."""
    # Read all necessary files
    fir_data = read_json_file(FIR_FILE)
    statement_data = read_json_file(VICTIM_STATEMENT_FILE)
    victim_medical_data = read_json_file(VICTIM_MEDICAL_REPORT_FILE)
    accused_medical_data = read_json_file(ACCUSED_MEDICAL_REPORT_FILE)
    sop_rules = read_json_file(SOP_FILE)

    if not sop_rules:
        print("Error: The SOP file (rules_output.json) could not be read. Exiting.")
        return
        
    # Determine if the victim is a minor
    victim_age = get_victim_age(statement_data, victim_medical_data)
    #victim_age=23
    is_minor = victim_age < 18 if victim_age is not None else None

    # Process the data
    pocso_completed, pocso_incomplete, general_completed, general_incomplete = check_sop_compliance(
        fir_data, statement_data, victim_medical_data, accused_medical_data, sop_rules, is_minor
    )
    
    # Generate the new Markdown checklist
    checklist_md = generate_checklist_md(
        pocso_completed, pocso_incomplete, general_completed, general_incomplete, is_minor
    )
    
    # Generate other reports
    case_diary = generate_case_diary(fir_data, statement_data, victim_medical_data, accused_medical_data)
    final_report = generate_final_report(
        pocso_completed, pocso_incomplete, general_completed, general_incomplete, case_diary, is_minor
    )

    # Write the output files
    with open(CHECKLIST_FILE, 'w', encoding='utf-8') as f:
        f.write(checklist_md)

    with open(CASE_DIARY_FILE, 'w', encoding='utf-8') as f:
        f.write(case_diary)

    with open(FINAL_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print("Script finished successfully. Output files have been updated/generated:")
    print(f"- {CHECKLIST_FILE} (New interactive checklist)")
    print(f"- {CASE_DIARY_FILE}")
    print(f"- {FINAL_REPORT_FILE}")

if __name__ == "__main__":
    main()

