import os
import json
import logging
from utils import load_file, save_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Update file paths
PROMPT_FILE = os.path.join(PROJECT_ROOT, 'Prompts', 'Write_Literature_Summary.md')
TARGETED_BIBLIOGRAPHIES_DIR = os.path.join(PROJECT_ROOT, 'Targeted_Bibliographies')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'Inputs_and_Outputs', 'Literature_ProSummary')

def load_json_files(directory):
    json_data = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    json_data[os.path.splitext(file)[0]] = json.load(f)
    return json_data

def generate_literature_summary(prompt_file, json_data, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info("Created output directory: %s", output_dir)
    
    prompt = load_file(prompt_file)
    
    for bibliography_name, bibliography_data in json_data.items():
        try:
            summary_content = f"""
{prompt}

Here is the bibliographic data to summarize:
{json.dumps(bibliography_data, indent=2)}

Please generate a comprehensive literature summary based on the prompt and the provided bibliographic data.
"""
            output_file_name = f"{bibliography_name}_summary.md"
            output_file_path = os.path.join(output_dir, output_file_name)
            save_file(summary_content, output_file_path)
            logger.info("Saved literature summary prompt for %s to %s", bibliography_name, output_file_path)
        except Exception as e:
            logger.error("Failed to generate literature summary for %s: %s", bibliography_name, str(e))

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info("Created output directory: %s", OUTPUT_DIR)

    json_data = load_json_files(TARGETED_BIBLIOGRAPHIES_DIR)
    logger.info("Loaded %d JSON files from %s", len(json_data), TARGETED_BIBLIOGRAPHIES_DIR)

    generate_literature_summary(PROMPT_FILE, json_data, OUTPUT_DIR)

    logger.info("Process completed. Check logs for results.")

if __name__ == "__main__":
    main()