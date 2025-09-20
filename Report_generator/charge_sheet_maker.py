import re
from datetime import datetime
import os

# Define the input and output file paths
CASE_DIARY_FILE = "case_diary.txt"
FINAL_REPORT_FILE = "final_report.txt"
CHARGESHEET_FILE = "chargesheet.txt"

def read_file(file_path):
    """Reads the entire content of a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found. Please run the main script first.")
        return None

def parse_case_diary(diary_content):
    """Parses the case diary to extract key information."""
    details = {}
    
    # Using regex to find the required fields. 're.DOTALL' allows '.' to match newlines.
    details['police_station'] = (re.search(r"Police Station:\s*(.*?)\n", diary_content) or [None, "N/A"])[1]
    details['fir_no'] = (re.search(r"FIR No:\s*(.*?)\n", diary_content) or [None, "N/A"])[1]
    
    complainant_match = re.search(r"Complainant/Informant Details:\n\s*Name:\s*(.*?)\n\s*Address:\s*(.*?)\n", diary_content, re.DOTALL)
    if complainant_match:
        details['complainant_name'] = complainant_match.group(1).strip()
        details['complainant_address'] = complainant_match.group(2).strip()
    else:
        details['complainant_name'] = "N/A"
        details['complainant_address'] = "N/A"
        
    accused_match = re.search(r"Accused Details:\n\s*Accused 1:\n\s*Name:\s*(.*?)\n\s*Address:\s*(.*?)\n", diary_content, re.DOTALL)
    if accused_match:
        details['accused_name'] = accused_match.group(1).strip()
        details['accused_address'] = accused_match.group(2).strip()
    else:
        details['accused_name'] = "N/A"
        details['accused_address'] = "N/A"
        
    return details

def parse_final_report(report_content):
    """Parses the final report to extract the brief facts and other summaries."""
    summaries = {}
    
    # Extract the full case diary section from the final report to get combined facts
    case_diary_section_match = re.search(r"2\. Case Diary:\n\n(.*?)$", report_content, re.DOTALL)
    if case_diary_section_match:
        case_diary_text = case_diary_section_match.group(1)
        
        # Extract individual summaries from the case diary text
        summaries['brief_facts'] = (re.search(r"Brief Facts from FIR:\n\s*(.*?)\n\n", case_diary_text, re.DOTALL) or [None, "N/A"])[1].strip()
        summaries['victim_statement'] = (re.search(r"Victim's Statement Summary:\n\s*(.*?)\n\n", case_diary_text, re.DOTALL) or [None, "N/A"])[1].strip()
        summaries['victim_medical'] = (re.search(r"Medical Examination Summary \(Victim\):\n\s*Provisional Opinion:\s*(.*?)\n\n", case_diary_text, re.DOTALL) or [None, "N/A"])[1].strip()
        summaries['accused_medical'] = (re.search(r"Medical Examination Summary \(Accused\):\n\s*Provisional Opinion:\s*(.*?)\n\n", case_diary_text, re.DOTALL) or [None, "N/A"])[1].strip()
    else:
        summaries = {key: "N/A" for key in ['brief_facts', 'victim_statement', 'victim_medical', 'accused_medical']}

    return summaries


def generate_chargesheet(case_details, report_summaries):
    """Generates a text-based chargesheet from the parsed data."""
    
    # Get current date details
    now = datetime.now()
    current_date = now.strftime('%d/%m/%Y')
    current_year = now.year

    chargesheet = f"""
GOA POLICE
FINAL FORM/REPORT
(Under Section 193 BNSS)

BICHOLIM POLICE STATION
OUTWARD No. ______ DATE: {current_date}

IN THE COURT OF HON. PRESIDENT, CHILDREN'S COURT FOR THE STATE OF GOA AT PANAJI

1. *Dist. NORTH GOA *P.S. {case_details.get('police_station', 'N/A')}
   *Year {current_year} FIR NO: {case_details.get('fir_no', 'N/A')} *Date [Date of FIR]

2. Final Report/Charge Sheet No. ______ * Date {current_date}

4. (i) Acts & Sections: [List of Acts and Sections e.g., BNS, POCSO]
   
5. * Type of Final Report: Charge sheet

8. Name of the I.O: [Name of Investigating Officer]

9. Name of the complainant/Informant: {case_details.get('complainant_name', 'N/A')}
   Address: {case_details.get('complainant_address', 'N/A')}

11. Particulars of accused person charge sheeted:
    (i) * Name: {case_details.get('accused_name', 'N/A')}
    (v) Nationality: Indian
    (viii) Occupation: [Occupation of Accused]
    (ix) Address: {case_details.get('accused_address', 'N/A')}
    (xiv) Date of Arrest: [Date of Arrest]
    (xvii) Under Acts & Sections: [List of Acts and Sections]

13. Particulars of the witnesses to be examined:
    [List of witnesses to be populated based on investigation]
    1. {case_details.get('complainant_name', 'N/A')} (Complainant)
    2. [Doctor from Victim's Medical Report]
    3. [Doctor from Accused's Medical Report]
    4. [Other relevant witnesses]

16.* Brief Facts of the case:
MAY IT PLEASE YOUR HONOUR,

{report_summaries.get('brief_facts', 'N/A')}

During the course of the investigation, the statement of the victim was recorded, which is summarized as follows:
{report_summaries.get('victim_statement', 'N/A')}

Medical examinations of the victim and the accused were conducted. The provisional opinion from the victim's medical report states: "{report_summaries.get('victim_medical', 'N/A')}"
The provisional opinion from the accused's medical report states: "{report_summaries.get('accused_medical', 'N/A')}"

Based on the investigation, evidence collected, and statements recorded, it has been established that the accused committed the aforementioned offenses.

Hence the charge.

Signature of the Investigating Officer
Name: [Name of I.O.]
Rank: [Rank of I.O.]
"""
    return chargesheet.strip()

def main():
    """Main function to orchestrate the chargesheet generation."""
    case_diary_content = read_file(CASE_DIARY_FILE)
    final_report_content = read_file(FINAL_REPORT_FILE)
    
    if not all([case_diary_content, final_report_content]):
        print("One or more input files are missing. Cannot generate chargesheet.")
        return
        
    # Parse the necessary details from the files
    case_details = parse_case_diary(case_diary_content)
    report_summaries = parse_final_report(final_report_content)
    
    # Generate the chargesheet text
    chargesheet_text = generate_chargesheet(case_details, report_summaries)
    
    # Write the output file
    with open(CHARGESheet_FILE, 'w', encoding='utf-8') as f:
        f.write(chargesheet_text)
        
    print(f"Script finished successfully. Chargesheet generated at: {CHARGESHEET_FILE}")

if __name__ == "__main__":
    main()
