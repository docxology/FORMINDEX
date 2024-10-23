import os
import json
import time
from openai import OpenAI
from datetime import datetime
import glob
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger = logging.getLogger('')
    logger.handlers = [console_handler]
    return logger

logger = setup_logging()

# Specify target System prompt by short name
TARGET_SYSTEM_PROMPT = "donor_insight_researcher"

def load_api_key(key_file_path):
    try:
        with open(key_file_path, 'r') as key_file:
            keys = key_file.read().strip().split('\n')
            api_keys = dict(key.split('=') for key in keys)
            perplexity_api_key = api_keys.get('PERPLEXITY_API_KEY')
        
        if not perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in the key file")
        
        logger.info("Perplexity API Key loaded successfully")
        return perplexity_api_key
    except FileNotFoundError:
        logger.error(f"API key file not found at {key_file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading API key: {str(e)}")
        raise

def load_json_file(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"{file_path} file not found")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding {file_path} file")
        raise

# Function to get system message based on short_name
def get_system_message(system_prompts, short_name):
    system_prompt = next((prompt for prompt in system_prompts.values() if prompt["short_name"] == short_name), None)
    if not system_prompt:
        logger.warning(f"System prompt with short_name '{short_name}' not found. Using default.")
        system_prompt = system_prompts["default"]
    return {
        "role": "system",
        "content": system_prompt["description"]
    }

def process_person_research(client, system_prompts, person_data, base_output_dir):
    short_name = person_data["short_name"]
    prompt = person_data["prompt"]
    
    output_file = os.path.join(base_output_dir, f"{short_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    existing_files = glob.glob(os.path.join(base_output_dir, f"{short_name}*.md"))
    
    if existing_files:
        logger.info(f"Skipping research for {short_name}: Output already exists.")
        return

    messages = [
        get_system_message(system_prompts, TARGET_SYSTEM_PROMPT),
        {
            "role": "user",
            "content": prompt,
        },
    ]

    logger.info(f"\nProcessing research for: {short_name}")
    logger.info(f"Prompt: {prompt[:100]}...")

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=messages,
        )
        
        content = response.choices[0].message.content

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        end_time = time.time()
        elapsed_time = end_time - start_time

        with open(output_file, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)

        logger.info(f"Research completed successfully.")
        logger.info(f"Time taken: {elapsed_time:.2f} seconds")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Number of lines in output: {line_count}")

    except Exception as e:
        logger.error(f"Error processing research: {str(e)}")

    logger.info("---")
    time.sleep(1)

def main():
    base_output_dir = "People_Research"
    os.makedirs(base_output_dir, exist_ok=True)

    key_file_path = "RR_LLM_keys.key"  # Updated key file name and location
    PERPLEXITY_API_KEY = load_api_key(key_file_path)

    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

    people_prompts = load_json_file("RR_People_Prompts.json")
    system_prompts = load_json_file("RR_System_Prompts.json")

    for person_id, person_data in people_prompts.items():
        process_person_research(client, system_prompts, person_data, base_output_dir)

    logger.info("All person research completed.")

if __name__ == "__main__":
    main()
