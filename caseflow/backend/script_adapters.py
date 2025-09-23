"""
Script wrappers for existing Python modules to adapt them to the new case-based structure.
These wrappers handle path management and provide consistent interfaces.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parsers and generators to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / 'parsers'))
sys.path.append(str(current_dir / 'generators'))

class ConfigManager:
    """Manages configuration for OCR and file paths"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def create_temp_config(self, input_dir: str, output_dir: str) -> str:
        """Create a temporary config file for the parsers"""
        config_content = f"""
# Temporary configuration for CaseFlow
ocr_space_api_key: "{self.api_key}"

paths:
  input_directory: "{input_dir}"
  output_directory: "{output_dir}"
"""
        
        # Create temp config file
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_config.write(config_content)
        temp_config.close()
        
        return temp_config.name

def adapt_compliance_generator(json_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Adapt the compliance generator to work with case-specific paths
    """
    try:
        # Import the compliance generator functions
        from compliance_checklist_generator import (
            read_json_file, check_sop_compliance, generate_checklist_md, get_victim_age
        )
        
        # Load input files
        fir_data = read_json_file(str(json_dir / "fir.json"))
        statement_data = read_json_file(str(json_dir / "statement.json"))
        victim_medical_data = read_json_file(str(json_dir / "victim_med_rep.json"))
        accused_medical_data = read_json_file(str(json_dir / "accused_med_rep.json"))
        
        # Load SOP rules from the backend directory
        rules_path = Path(__file__).parent / 'generators' / 'rules_output.json'
        sop_rules = read_json_file(str(rules_path))
        
        if not sop_rules:
            raise Exception("SOP rules file could not be loaded")
        
        # Determine if victim is minor
        victim_age = get_victim_age(statement_data or {}, victim_medical_data or {})
        is_minor = victim_age < 18 if victim_age is not None else None
        
        # Perform compliance check
        pocso_completed, pocso_incomplete, general_completed, general_incomplete = check_sop_compliance(
            fir_data, statement_data, victim_medical_data, accused_medical_data, sop_rules, is_minor
        )
        
        # Generate markdown content
        checklist_md_content = generate_checklist_md(
            pocso_completed, pocso_incomplete, general_completed, general_incomplete, is_minor
        )
        
        # Write to output directory
        output_file = output_dir / "compliance_checklist.md"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(checklist_md_content)
        
        return {
            "status": "success",
            "output_file": str(output_file),
            "content": checklist_md_content,
            "is_minor": is_minor
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def adapt_case_diary_generator(json_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Adapt the case diary generator to work with case-specific paths
    """
    try:
        from case_diary_generator import read_json_file, generate_case_diary
        
        # Load input files
        fir_data = read_json_file(str(json_dir / "fir.json"))
        statement_data = read_json_file(str(json_dir / "statement.json"))
        victim_medical_data = read_json_file(str(json_dir / "victim_med_rep.json"))
        accused_medical_data = read_json_file(str(json_dir / "accused_med_rep.json"))
        
        if not all([fir_data, statement_data]):
            raise Exception("Required JSON files (FIR, statement) are missing")
        
        # Generate case diary content
        case_diary_content = generate_case_diary(
            fir_data, statement_data, 
            victim_medical_data or {}, accused_medical_data or {}
        )
        
        # Write to output directory
        output_file = output_dir / "case_diary.txt"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(case_diary_content)
        
        return {
            "status": "success",
            "output_file": str(output_file),
            "content": case_diary_content
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def adapt_chargesheet_generator(json_dir: Path, diary_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Adapt the chargesheet generator to work with case-specific paths
    """
    try:
        from report_chargesheet_generator import (
            read_json_file, generate_final_report, generate_chargesheet
        )
        
        # Load input files
        fir_data = read_json_file(str(json_dir / "fir.json"))
        statement_data = read_json_file(str(json_dir / "statement.json"))
        victim_medical_data = read_json_file(str(json_dir / "victim_med_rep.json"))
        accused_medical_data = read_json_file(str(json_dir / "accused_med_rep.json"))
        
        # Load case diary content
        case_diary_file = diary_dir / "case_diary.txt"
        case_diary_content = ""
        if case_diary_file.exists():
            with open(case_diary_file, 'r', encoding='utf-8') as f:
                case_diary_content = f.read()
        
        # Generate final report
        final_report_content = generate_final_report(
            fir_data or {}, statement_data or {}, 
            victim_medical_data or {}, accused_medical_data or {},
            case_diary_content
        )
        
        # Generate chargesheet
        chargesheet_content = generate_chargesheet(
            final_report_content,
            statement_data or {},
            accused_medical_data or {},
            victim_medical_data or {},
            str(json_dir / "fir.json")
        )
        
        # Write output files
        output_dir.mkdir(parents=True, exist_ok=True)
        
        final_report_file = output_dir / "final_report.txt"
        chargesheet_file = output_dir / "chargesheet.md"
        
        with open(final_report_file, 'w', encoding='utf-8') as f:
            f.write(final_report_content)
        
        with open(chargesheet_file, 'w', encoding='utf-8') as f:
            f.write(chargesheet_content)
        
        return {
            "status": "success",
            "final_report_file": str(final_report_file),
            "chargesheet_file": str(chargesheet_file),
            "files": [
                {"name": "final_report.txt", "path": str(final_report_file)},
                {"name": "chargesheet.md", "path": str(chargesheet_file)}
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    # Test the script wrappers
    print("CaseFlow Script Wrappers - Testing functionality")
    
    # This can be used for debugging the wrappers
    test_json_dir = Path("./test_data/json")
    test_output_dir = Path("./test_data/output")
    
    if test_json_dir.exists():
        print("Testing compliance generator...")
        result = adapt_compliance_generator(test_json_dir, test_output_dir / "compliance")
        print(f"Result: {result['status']}")
        
        if result["status"] == "success":
            print("Testing case diary generator...")
            result2 = adapt_case_diary_generator(test_json_dir, test_output_dir / "diary")
            print(f"Result: {result2['status']}")
            
            if result2["status"] == "success":
                print("Testing chargesheet generator...")
                result3 = adapt_chargesheet_generator(
                    test_json_dir, 
                    test_output_dir / "diary", 
                    test_output_dir / "final"
                )
                print(f"Result: {result3['status']}")
    else:
        print("No test data found. Wrappers are ready for use.")