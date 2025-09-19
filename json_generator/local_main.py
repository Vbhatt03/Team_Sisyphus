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
from typing import Dict, Any, Optional

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
        from medical_records_parser import parse_medical_report
    except Exception as e:
        logger.error("Failed to import parse_medical_report: %s", e)
        parse_medical_report = None

try:
    from statement_parser import parse_statement_document
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


def main(file_map: Optional[Dict[str, Optional[str]]] = None, output_path: str = "case_data.json"):
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
    for doc_type, path in file_map.items():
        parser = parser_map.get(doc_type)
        if parser is None:
            logger.warning("No parser available for '%s'. Skipping.", doc_type)
            combined_results[doc_type] = {"error": "parser_not_available"}
            continue

        if not path:
            logger.warning("No file path for '%s'. Skipping.", doc_type)
            combined_results[doc_type] = {"error": "file_path_missing"}
            continue

        p = Path(path)
        if not p.exists():
            logger.warning("File for '%s' not found at %s. Skipping.", doc_type, path)
            combined_results[doc_type] = {"error": "file_not_found", "file_path": str(p)}
            continue

        outcome = _safe_call_parser(parser, str(p))
        combined_results[doc_type] = outcome.get("result") if "result" in outcome else {"error": outcome.get("error")}

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
    parser.add_argument("--medical", type=str, help="Medical report PDF path (overrides default).")
    parser.add_argument("--statement", type=str, help="Statement PDF path (overrides default).")
    parser.add_argument("--output", "-o", type=str, default="case_data.json", help="Output JSON file path.")
    args = parser.parse_args()

    file_map = {
        "fir": args.fir or None,
        "medical_report": args.medical or None,
        "statement": args.statement or None
    }

    main(file_map, output_path=args.output)
