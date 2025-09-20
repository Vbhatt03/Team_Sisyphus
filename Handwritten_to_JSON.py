import json
import re
from PIL import Image
from pdf2image import convert_from_path
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
# --- Configuration ---
# This is the free, open-source model we will use.
# It will be downloaded automatically the first time you run the script.
MODEL_ID = "llava-hf/llava-1.5-7b-hf"
VICTIM_PDF_PATH = 'victim report to PDF 20250907 12.57.07.pdf'
OUTPUT_JSON_PATH = 'victim_report_ai_extracted.json'

def initialize_model():
    """
    Initializes and loads the multimodal AI model and processor.
    Uses GPU if available, otherwise falls back to CPU.
    """
    print("Initializing AI model... (This may take a few minutes on first run as the model is downloaded)")
    
    # Check for GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load the model with 4-bit quantization to save memory
    model = LlavaForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        load_in_4bit=True
    )
    
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    
    print("Model initialized successfully.")
    return model, processor, device

def ask_model(prompt, image, model, processor, device):
    """
    Shows an image and a text prompt to the AI model and gets an answer.
    """
    full_prompt = f"USER: <image>\n{prompt} ASSISTANT:"
    
    inputs = processor(text=full_prompt, images=image, return_tensors="pt").to(device)

    # Generate an answer
    generate_ids = model.generate(**inputs, max_new_tokens=100)
    
    # Decode the answer and clean it up
    response_text = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    
    # Extract only the assistant's part of the response
    assistant_response = response_text.split("ASSISTANT:")[-1].strip()
    return assistant_response

def main():
    """
    Main function to process the PDF and extract information using the AI model.
    """
    model, processor, device = initialize_model()

    # Convert the first page of the PDF to an image
    print(f"Converting '{VICTIM_PDF_PATH}' to an image...")
    try:
        image = convert_from_path(VICTIM_PDF_PATH, first_page=1, last_page=1)[0]
    except Exception as e:
        print(f"Error converting PDF. Make sure you have poppler installed. Error: {e}")
        return

    # Define the questions to ask the AI for each field
    extraction_prompts = {
        "name": "Look at section 2 of the form. What is the patient's Name?",
        "age": "Look at section 4 of the form. What is the Age (as reported)?",
        "address": "Look at section 3 of the form. What is the Address?",
        "mlc_no": "Look at section 9 of the form. What is the MLC No.?",
        "police_station": "Look at section 9 of the form. What is the Police Station?",
        "history_of_violence": "Read section 15 A (vii), 'Description of incident in the words of the narrator'. Summarize this history.",
        "provisional_medical_opinion": "Read section 22, 'Provisional medical opinion'. Summarize the doctor's opinion."
    }

    extracted_data = {
        "report_type": "Victim Medico-Legal Examination (AI Extracted)",
    }

    print("\nStarting AI extraction process...")
    for field, prompt_text in extraction_prompts.items():
        print(f"  > Extracting '{field}'...")
        answer = ask_model(prompt_text, image, model, processor, device)
        extracted_data[field] = answer
        print(f"    - Got: {answer[:80]}...") # Print a snippet of the answer

    # Save the final structured data to a JSON file
    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(extracted_data, f, indent=2)
        
    print(f"\nExtraction complete. Cleaned data saved to '{OUTPUT_JSON_PATH}'")


if __name__ == "__main__":
    main()
