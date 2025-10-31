import os
import re
import logging
from pathlib import Path

# Define directories
LOG_DIR = Path.home() / 'Documents' / 'redaction_logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'redaction.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
    ]
)

# Define names to redact (case-insensitive)
NAMES_TO_REDACT = [
    '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', 
    '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]',
    '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]',
    '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]', '[REDACTED_NAME]'
]

# Hardcoded directories
INPUT_DIR = r''
OUTPUT_DIR = r''

def redact_text(text, file_path):
    """Redact file paths and specific names from text."""
    redactions = {}
    redacted_text = text
    
    # Improved file path redaction
    file_paths = re.finditer(
        r'(?i)(?<![A-Za-z0-9])([A-Z]:[\\/](?:[^\\/:*?"<>|\r\n]+[\\/])*[^\\/:*?"<>|\r\n]*)',
        text
    )
    
    for match in file_paths:
        path = match.group(1)
        if path and path.strip() and path not in redactions:
            if len(path) > 3 or (len(path) == 3 and path[1:3] == ':\\'):
                redactions[path] = '[REDACTED_FILE_PATH]'
                redacted_text = re.sub(
                    r'\b' + re.escape(path) + r'\b',
                    '[REDACTED_FILE_PATH]',
                    redacted_text
                )
    
    # Redact names (case-insensitive)
    for name in NAMES_TO_REDACT:
        pattern = r'\b' + re.escape(name) + r'\b'
        matches = re.finditer(pattern, redacted_text, re.IGNORECASE)
        for match in matches:
            original = match.group(0)
            if original not in redactions:
                redactions[original] = '[REDACTED_NAME]'
                redacted_text = re.sub(
                    r'\b' + re.escape(original) + r'\b',
                    '[REDACTED_NAME]',
                    redacted_text,
                    flags=re.IGNORECASE
                )
    
    return redacted_text, redactions

def process_file(input_path, output_path):
    """Process a single file and write redacted version to output path."""
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read input file
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Redact sensitive information
        redacted_content, redactions = redact_text(content, str(input_path))
        
        # Always write the file, even if no redactions were made
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(redacted_content)
        
        if redactions:
            logging.info(f"Redacted {len(redactions)} items in {input_path}")
            for original, replacement in redactions.items():
                logging.info(f"  - Replaced: {original} -> {replacement}")
            return len(redactions)
        else:
            logging.info(f"No redactions made in {input_path} (file copied as-is)")
            return 0
    
    except Exception as e:
        logging.error(f"Error processing {input_path}: {str(e)}")
        return 0

def main():
    try:
        input_path = Path(INPUT_DIR)
        output_path = Path(OUTPUT_DIR)
        
        if not input_path.exists():
            logging.error(f"Input directory does not exist: {input_path}")
            return
        
        processed_files = 0
        redaction_count = 0
        
        # Process all files in input directory
        for root, _, files in os.walk(input_path):
            for filename in files:
                input_file = Path(root) / filename
                relative_path = input_file.relative_to(input_path)
                output_file = output_path / relative_path
                
                logging.info(f"Processing: {input_file}")
                redactions = process_file(input_file, output_file)
                
                if redactions > 0:
                    processed_files += 1
                    redaction_count += redactions
                else:
                    processed_files += 1  # Count files even if no redactions
        
        logging.info(f"Process complete! Processed {processed_files} files, redacted {redaction_count} items total.")
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        logging.info("Redaction process completed.")

if __name__ == "__main__":
    logging.info("Starting redaction process...")

    main()
