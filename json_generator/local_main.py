import json
import logging
import yaml
from pathlib import Path

# Import the primary processing function from each refactored parser module.
# This works because each parser file now has a dedicated function for this purpose.
from fir_parser import process_fir_pdf
from statement_doc_parser import process_statement_pdf
from medical_report_parser import process_medical_pdf

# --- Configuration ---
CONFIG_FILE = "config.yaml"

# Configure logging for clear, informative output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path: str) -> dict | None:
    """Loads the entire configuration from the YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at '{config_path}'.")
        logging.error("Please ensure 'config.yaml' exists in the same directory.")
        return None
    except Exception as e:
        logging.error(f"Error reading or parsing the config file: {e}")
        return None

def main():
    """
    Main orchestrator to run the entire PDF parsing pipeline.
    """
    logging.info("--- Starting Document Processing Pipeline ---")
    
    # 1. Load all settings from the config file
    config = load_config(CONFIG_FILE)
    if not config:
        return

    # 2. Extract API key and paths from the loaded config
    api_key = config.get('ocr_space_api_key')
    paths = config.get('paths', {})
    pdf_directory = paths.get('input_directory')
    output_directory = paths.get('output_directory')

    # 3. Validate that all required configurations are present
    if not all([api_key, pdf_directory, output_directory]):
        logging.error("A required setting (ocr_space_api_key, input_directory, or output_directory) is missing from 'config.yaml'.")
        return
    if "YOUR" in api_key or not api_key.strip():
        logging.error("API key in 'config.yaml' is a placeholder or empty. Please provide a valid key.")
        return
        
    pdf_dir = Path(pdf_directory)
    output_dir = Path(output_directory)

    # 4. Set up directories
    if not pdf_dir.is_dir():
        logging.error(f"Input directory not found: '{pdf_dir}'. Please check the path in 'config.yaml'.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Input directory:  '{pdf_dir.resolve()}'")
    logging.info(f"Output directory: '{output_dir.resolve()}'")

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logging.warning(f"No PDF files found in '{pdf_dir}'.")
        return

    logging.info(f"Found {len(pdf_files)} PDF(s) to process.")

    # 5. Define the routing map: keywords in filenames map to parser functions
    parser_map = {
        "fir": process_fir_pdf,
        "statement": process_statement_pdf,
        "medical": process_medical_pdf,
        "victim": process_medical_pdf,
        "accuse": process_medical_pdf,
    }

    # 6. Process each PDF file individually
    success_count = 0
    failure_count = 0
    for pdf_path in pdf_files:
        try:
            logging.info(f"--- Processing: {pdf_path.name} ---")
            filename_lower = pdf_path.name.lower()
            
            selected_parser = None
            for keyword, parser_func in parser_map.items():
                if keyword in filename_lower:
                    selected_parser = parser_func
                    logging.info(f"Keyword '{keyword}' matched. Using parser: {parser_func.__name__}")
                    break
            
            if selected_parser:
                # Execute the selected parser function
                parsed_data = selected_parser(str(pdf_path), api_key=api_key)
                
                # Save the output to a corresponding JSON file
                output_filename = pdf_path.stem + ".json"
                output_path = output_dir / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, indent=4, ensure_ascii=False)
                
                logging.info(f"✅ Successfully generated JSON: '{output_path}'")
                success_count += 1
            else:
                logging.warning(f"⚠️ No matching parser found for '{pdf_path.name}'. Skipping.")

        except Exception as e:
            logging.error(f"❌ An unexpected error occurred while processing '{pdf_path.name}': {e}", exc_info=True)
            failure_count += 1
            
    logging.info("--- Pipeline Finished ---")
    logging.info(f"Summary: {success_count} succeeded, {failure_count} failed.")

if __name__ == "__main__":
    main()