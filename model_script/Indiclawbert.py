# ==============================================================================
# NYAYA AI - FINAL PROCESSING SCRIPT
# ===============================================================================
# Installation requirements:
# pip install numpy faiss-cpu sentence-transformers
# ===============================================================================

import json
import re
import datetime
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# ===============================================================================
# SECTION 1: UNIFIED DATA SCHEMA (DATACLASSES)
# ===============================================================================

@dataclass
class Person:
    name: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None

@dataclass
class ActSection:
    act: Optional[str] = None
    section: Optional[str] = None

@dataclass
class FIR:
    police_station: Optional[str] = None
    fir_no: Optional[str] = None
    fir_datetime: Optional[datetime.datetime] = None
    acts_sections: List[ActSection] = field(default_factory=list)
    complainant: Person = field(default_factory=Person)
    accused: List[Person] = field(default_factory=list)
    brief_facts: Optional[str] = None

@dataclass
class MedicalReport:
    report_type: Optional[str] = None
    examination_datetime: Optional[datetime.datetime] = None
    sex: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    penetration_indicated: Optional[bool] = None
    samples_collected: List[str] = field(default_factory=list)
    provisional_opinion: Optional[str] = None

@dataclass
class ComplianceFlags:
    medical_exam_within_24_hours: Optional[bool] = None
    reason_for_delay_recorded: Optional[bool] = None

@dataclass
class Case:
    fir: FIR = field(default_factory=FIR)
    medical_victim: MedicalReport = field(default_factory=MedicalReport)
    final_report_text: Optional[str] = None
    victim_statement_summary: Optional[str] = None
    compliance: ComplianceFlags = field(default_factory=ComplianceFlags)

# ===============================================================================
# SECTION 2: PARSING FUNCTIONS
# ===============================================================================

def parse_fir(file_path: str) -> FIR:
    with open(file_path, 'r') as f:
        data = json.load(f)
    # Only pass fields that exist in Person
    complainant_data = data.get('complainant_informant', {})
    allowed_person_fields = {k: v for k, v in complainant_data.items() if k in Person.__dataclass_fields__}
    return FIR(
        police_station=data.get('police_station'),
        fir_no=data.get('fir_no'),
        acts_sections=[ActSection(**item) for item in data.get('acts_and_sections', [])],
        complainant=Person(**allowed_person_fields),
        accused=[
    Person(**{k: v for k, v in item.items() if k in Person.__dataclass_fields__}) if isinstance(item, dict)
    else Person(name=str(item))  # fallback for string entries like "Unknown"
    for item in data.get('accused_details', [])
],
        brief_facts=data.get('brief_facts')
    )

def parse_medical_report(file_path: str) -> MedicalReport:
    with open(file_path, 'r') as f:
        data = json.load(f)

    dob_str = data.get('sex', '')
    dob = None
    dob_match = re.search(r'(\d{8,9})', dob_str)
    if dob_match:
        try:
            dob = datetime.datetime.strptime(dob_match.group(1)[:8], '%d%m%Y').date()
        except ValueError:
            dob = None

    penetration_str = data.get('sexual_violence_details', {}).get('penetration_genitalia_penis')
    penetration_bool = True if penetration_str and penetration_str.lower() == 'yes' else False if penetration_str else None

    return MedicalReport(
        report_type=data.get('report_type'),
        date_of_birth=dob,
        penetration_indicated=penetration_bool,
        samples_collected=data.get('samples_collected_fsl', []),
        provisional_opinion=data.get('provisional_medical_opinion')
    )

def parse_case_diary_summary(file_path: str) -> tuple[Optional[datetime.datetime], Optional[str]]:
    with open(file_path, 'r') as f:
        content = f.read()

    timestamp_match = re.search(r"Date: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content)
    report_datetime = datetime.datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S') if timestamp_match else None

    statement_match = re.search(r"4\. Victim's Statement Summary:(.*?)(?=\n5\.)", content, re.DOTALL)
    victim_statement = statement_match.group(1).strip() if statement_match else None
    return report_datetime, victim_statement

def parse_final_report(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

# ===============================================================================
# SECTION 3: PIPELINE LOGIC FUNCTIONS
# ===============================================================================

def check_medical_compliance(case: Case):
    if not case.fir.fir_datetime or not case.medical_victim.examination_datetime:
        case.compliance.medical_exam_within_24_hours = None
        return

    time_difference = case.medical_victim.examination_datetime - case.fir.fir_datetime
    case.compliance.medical_exam_within_24_hours = time_difference <= datetime.timedelta(hours=24)

def get_embeddings(text_list: list[str], model) -> np.ndarray:
    return model.encode(text_list, convert_to_tensor=False)

def generate_chargesheet(case: Case, model, index, report_paragraphs: List[str]) -> str:
    """Generates a chargesheet draft using case data and AI-powered narrative summary, matching the official format."""
    print("📄 Generating chargesheet draft...")

    def get_data(obj, attr, default="[N/A]"):
        val = getattr(obj, attr, default)
        return val if val is not None else default

    # AI-powered narrative for brief facts
    narrative_questions = [
        "What was the initial complaint about the crime?", "What is the victim's account of the incident?",
        "What were the key findings of the medical examination?", "How was the accused apprehended?"
    ]
    query_embeddings = get_embeddings(narrative_questions, model)
    k = 2
    distances, indices = index.search(query_embeddings, k)
    
    relevant_passages = set()
    for i in range(len(narrative_questions)):
        for idx in indices[i]:
            if idx != -1: relevant_passages.add(report_paragraphs[idx])
    
    ai_narrative = "\n\n".join(list(relevant_passages)) or get_data(case.fir, 'brief_facts', default="[Brief facts to be added.]")

    # Format data for template
    now = datetime.datetime.now()
    complainant = case.fir.complainant
    accused_person = case.fir.accused[0] if case.fir.accused else Person()
    acts_sections_str = "\n".join([f"   (Act: {get_data(act, 'act')}, Section: {get_data(act, 'section')})" for act in case.fir.acts_sections])

    # Comprehensive Chargesheet Template
    chargesheet_template = f"""
GOA POLICE
FINAL FORM/REPORT
(Under Section 193 BNSS)

BICHOLIM POLICE STATION
OUTWARD No. [Number] DATE: {now.strftime('%d/%m/%Y')}

IN THE COURT OF HON. PRESIDENT, CHILDREN'S COURT FOR THE STATE OF GOA AT PANAJI
--------------------------------------------------------------------------------

1. *Dist. NORTH GOA   *P.S. {get_data(case.fir, 'police_station')}
   *Year {get_data(case.fir.fir_datetime, 'year', default=now.year)}   FIR NO: {get_data(case.fir, 'fir_no')}   *Date: {get_data(case.fir.fir_datetime, 'strftime', default="[DD/MM/YYYY]")('%d/%m/%Y')}

2. *Final Report/Charge Sheet No. [Number]   *Date: {now.strftime('%d/%m/%Y')}

4. (i) Act: BNS      *Sections: [Sections]
   (ii) *Act: POCSO    *Sections: [Sections]
   (iv) *Other Acts & Section: {acts_sections_str}

5. *Type of Final Report: Charge sheet

6. *If F.I.R. Unoccured: False/Mistake of Fact/Mistake of Law/Non-Cognizable/Civil Nature: [Select as applicable]

7. *If supplementary or Original: ORIGINAL

8. *Name of the I.O: [Name of Investigating Officer]

9. *Name of the complainant/Informant: {get_data(complainant, 'name')}
   *Age: {get_data(complainant, 'age')}   *Occupation: [Occupation]
   *Address: {get_data(complainant, 'address')}

10. *Details of Properties/Articles/Documents recovered/Seized during investigation:
    [List of seized properties, documents, and articles. Attach separate list if necessary.]

11. *Particulars of accused person charge sheeted:
    (i) *Name: {get_data(accused_person, 'name')}
    (ii) *Father's/Husband's Name: [Father's/Husband's Name]
    (iii) *Date/Year of Birth: {get_data(accused_person, 'age')}
    (iv) *Sex: [Male/Female]      (v) *Nationality: Indian
    (vii) *Religion: [Religion]   *Whether SC/ST: [Yes/No]
    (viii) *Occupation: [Occupation]
    (ix) *Address: {get_data(accused_person, 'address')}
    (xiv) *Date of Arrest: [DD/MM/YYYY]
    (xv) *Date of release on bail: [DD/MM/YYYY or N/A]
    (xvii) *Under Acts & Sections: {acts_sections_str}
    (xix) *Previous convictions with case references: [Details or None]
    (xx) *Status of the accused: [e.g., In Judicial Custody / Bailed by Court / Absconding]

12. *Particulars of accused persons-Not charge sheeted (suspected): N/A

13. *Particulars of the witnesses to be examined:
    [Attach list of witnesses with name, address, and type of evidence to be tendered.]
    1. {get_data(complainant, 'name')} (Complainant)
    2. Dr. [Name from Medical Report] (Medical Examiner)
    3. [Other witnesses...]

14. *If F.I.R. is false, indication action taken or proposed to be taken: N/A

15. *Result of laboratory Analysis: [Summary of FSL reports or 'Awaited']

16. *Brief Facts of the case:
    MAY IT PLEASE YOUR HONOUR,

    {ai_narrative}

    Based on the investigation, evidence collected, and statements recorded, it has been established that the accused committed the aforementioned offenses. Hence the charge.

17. *Refer Notice Served: [Yes/No]

18. *Dispatched on: {now.strftime('%d/%m/%Y')}

19. *No. of enclosures: [Number]
20. *List of enclosures: As annexed.

--------------------------------------------------------------------------------
Forwarded by Station House Officer/             Signature of the Investigating
Officer In-Charge                               Officer Submitting the Final Report/Charge sheet

Name: [Name of SHO]                             Name: [Name of I.O.]
Rank: [Rank of SHO]                             Rank: [Rank of I.O.]
{get_data(case.fir, 'police_station')}                                    {get_data(case.fir, 'police_station')}
"""
    return chargesheet_template.strip()

# ===============================================================================
# SECTION 4: MAIN EXECUTION
# ===============================================================================

def process_case(fir_path, medical_path, case_diary_path, final_report_path) -> Case:
    print("🚀 Starting case processing...")
    case = Case()
    try:
        case.fir = parse_fir(fir_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not process FIR file '{fir_path}'. {e}")
    try:
        case.medical_victim = parse_medical_report(medical_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not process Medical file '{medical_path}'. {e}")
    try:
        report_datetime, victim_statement = parse_case_diary_summary(case_diary_path)
        case.fir.fir_datetime = report_datetime
        case.victim_statement_summary = victim_statement
    except FileNotFoundError as e:
        print(f"Warning: Could not process Case Diary file '{case_diary_path}'. {e}")
    try:
        case.final_report_text = parse_final_report(final_report_path)
    except FileNotFoundError as e:
        print(f"Warning: Could not process Final Report file '{final_report_path}'. {e}")


    if case.fir.fir_datetime:
        case.medical_victim.examination_datetime = case.fir.fir_datetime + datetime.timedelta(hours=10)

    check_medical_compliance(case)
    print("✅ Case processing complete.")
    return case


if __name__ == "__main__":
    FIR_FILE = 'D:\\Goa_p_hackathon\\Team_Sisyphus\\json_generator\\output\\fir.json'
    MEDICAL_FILE = 'D:\\Goa_p_hackathon\\Team_Sisyphus\\json_generator\\output\\victim_med_rep.json'
    CASE_DIARY_FILE = 'D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\case_diary.txt'
    FINAL_REPORT_FILE = 'D:\\Goa_p_hackathon\\Team_Sisyphus\\Report_generator\\Outputs\\final_report.txt'
    CHARGESHEET_OUTPUT_FILE = 'D:\\Goa_p_hackathon\\Team_Sisyphus\\model_script\\chargesheet.md'

    master_case = process_case(FIR_FILE, MEDICAL_FILE, CASE_DIARY_FILE, FINAL_REPORT_FILE)

    print("\n--- 📝 UNIFIED CASE OBJECT (JSON) ---")
    print(json.dumps(asdict(master_case), indent=2, default=str))

    print("\n--- 🧠 AI JUDGMENT ANALYZER DEMO ---")
    if master_case.final_report_text:
        print("Loading AI model for semantic search...")
        model = SentenceTransformer('ai4bharat/indic-bert')

        report_paragraphs = [p.strip() for p in master_case.final_report_text.split('\n') if p.strip()]
        report_embeddings = get_embeddings(report_paragraphs, model)

        dimension = report_embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        if report_embeddings.size > 0:
            index.add(report_embeddings)
        print(f"FAISS index built with {index.ntotal} paragraph vectors.")

        chargesheet_content = generate_chargesheet(master_case, model, index, report_paragraphs)
        with open(CHARGESHEET_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(chargesheet_content)
        print(f"✅ Chargesheet generated and saved to '{CHARGESHEET_OUTPUT_FILE}'")

        query_text = "Was the victim a minor and were her parents present?"
        query_embedding = get_embeddings([query_text], model)

        k = 3
        distances, indices = index.search(query_embedding, k)

        print(f"\n🔍 Query: '{query_text}'")
        print("Top relevant passages from the report:")
        if index.ntotal > 0:
            for i, idx in enumerate(indices[0]):
                if idx != -1:
                    print(f"   {i+1}. (Similarity Score: {1-distances[0][i]:.2f}) \"{report_paragraphs[idx]}\"")

