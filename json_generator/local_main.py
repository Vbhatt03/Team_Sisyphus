#!/usr/bin/env python3
"""
local_main.py

Minimal, modular main script that imports parsing functions,
runs each parser on its file (paths configurable),
and writes a combined JSON file.

Note:
- extract_rules is intentionally not called here.
"""

from pathlib import Path
import logging
import json
import argparse
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import parser functions
try:
    from fir_parser import parse_fir_document
except Exception as e:
    logger.error("Failed to import parse_fir_document: %s", e)
    parse_fir_document = None

try:
    from medical_report_parser import parse_medical_report
except Exception:
    try:
        from medical_report_parser import parse_medical_report
    except Exception as e:
        logger.error("Failed to import parse_medical_report: %s", e)
        parse_medical_report = None

try:
    from statement_doc_parser import parse_statement_document
except Exception as e:
    logger.error("Failed to import parse_statement_document: %s", e)
    parse_statement_document = None


def _safe_call_parser(parser_func, file_path: str) -> Dict[str, Any]:
    """
    Call a parser function with robust error handling.

    Returns a dictionary with either 'result' or 'error' keys.
    """
    try:
        logger.info("Running parser %s on %s", getattr(parser_func, "__name__", str(parser_func)), file_path)
        parsed = parser_func(file_path)
        if parsed is None:
            parsed = {}
        return {"result": parsed}
    except Exception as e:
        logger.exception("Parser %s failed for %s: %s", getattr(parser_func, "__name__", "parser"), file_path, e)
        return {"error": str(e)}


def main(file_map: Optional[Dict[str, Optional[Any]]] = None, output_path: str = "case_data.json"):
    """
    Orchestrate parsing of multiple document types.

    Args:
        file_map: Optional mapping with keys 'fir', 'medical_report', 'statement'
                mapping to file paths (strings) or None. If None, uses defaults.
        output_path: Where to write the combined JSON.
    """
    defaults = {
        "fir": "FIR.pdf",
        "medical_report": "medical_report.pdf",
        "statement": "statement.pdf"
    }
    if file_map is None:
        file_map = defaults
    else:
        for k, v in defaults.items():
            file_map.setdefault(k, file_map.get(k) or v)

    parser_map = {
        "fir": parse_fir_document,
        "medical_report": parse_medical_report,
        "statement": parse_statement_document
    }

    combined_results: Dict[str, Any] = {}
    
    # Handle the single-file parsers
    for doc_type in ["fir", "statement"]:
        path = file_map.get(doc_type)
        parser = parser_map.get(doc_type)

        if not path or not parser:
            logger.warning("No path or parser for '%s'. Skipping.", doc_type)
            combined_results[doc_type] = {"error": "file_path_missing" if not path else "parser_not_available"}
            continue
        
        p = Path(path)
        if not p.exists():
            logger.warning("File for '%s' not found at %s. Skipping.", doc_type, path)
            combined_results[doc_type] = {"error": "file_not_found", "file_path": str(p)}
            continue
            
        outcome = _safe_call_parser(parser, str(p))
        combined_results[doc_type] = outcome.get("result") if "result" in outcome else {"error": outcome.get("error")}

    # Handle multiple medical reports
    medical_report_paths = file_map.get("medical_report")
    if medical_report_paths:
        combined_results["medical_reports"] = []
        parser = parser_map.get("medical_report")
        if not parser:
            combined_results["medical_reports"].append({"error": "parser_not_available"})
        else:
            # If a single path is given, it's a string; convert to list for iteration
            if isinstance(medical_report_paths, str):
                medical_report_paths = [medical_report_paths]

            for path in medical_report_paths:
                p = Path(path)
                if not p.exists():
                    logger.warning("Medical report file not found at %s. Skipping.", path)
                    combined_results["medical_reports"].append({"error": "file_not_found", "file_path": str(p)})
                    continue

                outcome = _safe_call_parser(parser, str(p))
                parsed_data = outcome.get("result") if "result" in outcome else {"error": outcome.get("error")}
                parsed_data["file_path"] = str(p)
                combined_results["medical_reports"].append(parsed_data)

    # Write JSON output
    out_path = Path(output_path)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(combined_results, f, indent=2, ensure_ascii=False)
        logger.info("Wrote combined results to %s", out_path)
    except Exception as e:
        logger.exception("Failed to write output JSON to %s: %s", out_path, e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modular main to parse legal/medical documents.")
    parser.add_argument("--fir", type=str, help="FIR PDF path (overrides default).")
    parser.add_argument("--medical", nargs='+', help="Medical report PDF paths (accepts multiple).")
    parser.add_argument("--statement", type=str, help="Statement PDF path (overrides default).")
    parser.add_argument("--output", "-o", type=str, default="case_data.json", help="Output JSON file path.")
    args = parser.parse_args()

    file_map = {
        "fir": args.fir,
        "medical_report": args.medical,
        "statement": args.statement
    }

    main(file_map, output_path=args.output)
