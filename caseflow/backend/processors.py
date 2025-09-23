import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import subprocess
import logging

# Add parsers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'parsers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'generators'))

from parsers.fir_parser import process_fir_pdf
from parsers.statement_doc_parser import process_statement_pdf  
from parsers.medical_report_parser import process_medical_pdf
from script_adapters import adapt_compliance_generator, adapt_case_diary_generator, adapt_chargesheet_generator

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def parse_uploaded_pdfs(self, case_dir: Path) -> Dict[str, Any]:
        """Parse all uploaded PDFs and generate JSON outputs"""
        uploads_dir = case_dir / "uploads"
        json_dir = case_dir / "outputs" / "json"
        json_dir.mkdir(parents=True, exist_ok=True)
        
        results = {"parsed_files": [], "errors": [], "logs": []}
        
        # Define file mappings
        file_mappings = {
            "fir.pdf": ("fir.json", process_fir_pdf),
            "statement.pdf": ("statement.json", process_statement_pdf),
            "victim_med.pdf": ("victim_med_rep.json", process_medical_pdf),
            "accused_med.pdf": ("accused_med_rep.json", process_medical_pdf),
        }
        
        for pdf_filename, (json_filename, parser_func) in file_mappings.items():
            pdf_path = uploads_dir / pdf_filename
            json_path = json_dir / json_filename
            
            if pdf_path.exists():
                try:
                    logger.info(f"Processing {pdf_filename}")
                    results["logs"].append(f"Processing {pdf_filename}")
                    
                    # Call the parser function
                    parsed_data = parser_func(str(pdf_path), api_key=self.api_key)
                    
                    # Save JSON output
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed_data, f, indent=4, ensure_ascii=False)
                    
                    results["parsed_files"].append({
                        "pdf_file": pdf_filename,
                        "json_file": json_filename,
                        "json_path": str(json_path),
                        "status": "success"
                    })
                    
                    logger.info(f"Successfully parsed {pdf_filename} -> {json_filename}")
                    results["logs"].append(f"✅ Successfully generated {json_filename}")
                    
                except Exception as e:
                    error_msg = f"Failed to parse {pdf_filename}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["logs"].append(f"❌ {error_msg}")
            else:
                # Skip missing optional files
                if pdf_filename in ["victim_med.pdf", "accused_med.pdf"]:
                    results["logs"].append(f"⚠️ {pdf_filename} not found (optional)")
                else:
                    error_msg = f"Required file {pdf_filename} not found"
                    results["errors"].append(error_msg)
                    results["logs"].append(f"❌ {error_msg}")
        
        return results

class ComplianceGenerator:
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.json_dir = case_dir / "outputs" / "json"
        self.compliance_dir = case_dir / "outputs" / "compliance"
        self.compliance_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_compliance_checklist(self) -> Dict[str, Any]:
        """Generate compliance checklist using the compliance generator"""
        try:
            result = adapt_compliance_generator(self.json_dir, self.compliance_dir)
            
            if result["status"] == "success":
                # Parse the content into checklist items
                checklist_items = self._parse_markdown_to_items(result["content"])
                result["checklist_items"] = checklist_items
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate compliance checklist: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _parse_markdown_to_items(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Parse markdown checklist into structured items"""
        items = []
        current_section = ""
        
        for line in markdown_content.split('\n'):
            line = line.strip()
            
            # Detect section headers
            if line.startswith('#'):
                current_section = line.replace('#', '').strip()
            
            # Detect checklist items
            elif line.startswith('- [ ]') or line.startswith('- [x]'):
                checked = '[x]' in line
                text = line.replace('- [ ]', '').replace('- [x]', '').strip()
                
                if text:  # Skip empty items
                    items.append({
                        "section": current_section,
                        "text": text,
                        "checked": checked
                    })
        
        return items

class CaseDiaryGenerator:
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.json_dir = case_dir / "outputs" / "json"
        self.diary_dir = case_dir / "outputs" / "case_diary"
        self.diary_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_case_diary(self) -> Dict[str, Any]:
        """Generate case diary using the case diary generator"""
        try:
            result = adapt_case_diary_generator(self.json_dir, self.diary_dir)
            
            if result["status"] == "success":
                # Split into pages (simple approach - split by sections)
                pages = self._split_content_into_pages(result["content"])
                result["pages"] = pages
                result["total_pages"] = len(pages)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate case diary: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _split_content_into_pages(self, content: str) -> List[Dict[str, Any]]:
        """Split case diary content into pages"""
        # Simple splitting by numbered sections
        pages = []
        current_page = ""
        page_num = 1
        
        lines = content.split('\n')
        for line in lines:
            current_page += line + '\n'
            
            # Start new page after certain patterns (adjust as needed)
            if line.strip() and (
                'Medical Examination Summary' in line or
                'Brief Facts' in line or
                len(current_page) > 2000  # Max chars per page
            ):
                if current_page.strip():
                    pages.append({
                        "page_number": page_num,
                        "content": current_page.strip()
                    })
                    page_num += 1
                    current_page = ""
        
        # Add final page if any content remains
        if current_page.strip():
            pages.append({
                "page_number": page_num,
                "content": current_page.strip()
            })
        
        return pages if pages else [{"page_number": 1, "content": content}]

class ChargesheetGenerator:
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.json_dir = case_dir / "outputs" / "json"
        self.diary_dir = case_dir / "outputs" / "case_diary"
        self.final_dir = case_dir / "outputs" / "final"
        self.final_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_chargesheet(self) -> Dict[str, Any]:
        """Generate final report and chargesheet"""
        try:
            result = adapt_chargesheet_generator(self.json_dir, self.diary_dir, self.final_dir)
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate chargesheet: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }