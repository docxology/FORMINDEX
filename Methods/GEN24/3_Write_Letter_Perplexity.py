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

def load_api_key(key_file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file_path = os.path.join(script_dir, key_file_name)
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

def load_system_prompts():
    system_prompts = load_json_file("RR_System_Prompts.json")
    logger.info(f"Loaded {len(system_prompts)} system prompts")
    return system_prompts

def get_system_message(system_prompts, short_name):
    system_prompt = next((prompt for prompt in system_prompts.values() if prompt["short_name"] == short_name), None)
    if not system_prompt:
        logger.warning(f"System prompt with short_name '{short_name}' not found. Using default.")
        system_prompt = system_prompts["default"]
    return {
        "role": "system",
        "content": system_prompt["description"]
    }

def load_organization_file(org_folder):
    py_files = glob.glob(os.path.join(org_folder, '*.py'))
    if not py_files:
        logger.error(f"No .py file found in {org_folder}")
        return None, 0
    with open(py_files[0], 'r') as f:
        content = f.read()
        line_count = len(content.splitlines())
    logger.info(f"Loaded organization file from {org_folder} with {line_count} lines")
    return content, line_count

def process_introduction_package(client, system_prompts, org_content, research_content, person_name, org_name, org_line_count):
    output_folder = os.path.join("Introductions", org_name)
    os.makedirs(output_folder, exist_ok=True)
    
    # Check if a letter for this combination already exists
    existing_files = glob.glob(os.path.join(output_folder, f"{org_name}_to_{person_name.replace(' ', '_')}*.md"))
    if existing_files:
        logger.info(f"Skipping {org_name} to {person_name}: Letter already exists")
        return False

    system_message = get_system_message(system_prompts, "letter_writer")
    user_content = f"""Organization Information ({org_line_count} lines):

{org_content}

Person Research:

{research_content}

Instructions:
1. Ensure you include at least 5-7 relevant quotes from {person_name}, properly cited.
2. Use a minimum of 15 unique sources for citations throughout the package.
3. Propose 3-5 specific, actionable engagement opportunities.
4. Include 2 hypothetical data visualizations or tables demonstrating alignment.
5. Demonstrate deep listening by referencing specific events or lesser-known facts about {person_name}'s philanthropic journey.
"""
    
    messages = [
        system_message,
        {
            "role": "user",
            "content": user_content,
        },
    ]

    logger.info(f"\nProcessing Introduction Package:")
    logger.info(f"From: {org_name} ({org_line_count} lines of context)")
    logger.info(f"To: {person_name}")
    logger.info(f"System Prompt: {system_message['content'][:100]}...")
    
    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=messages,
            max_tokens=16000, 
            temperature=0.6,
        )
        
        content = response.choices[0].message.content

        output_file = os.path.join(output_folder, f"{org_name}_to_{person_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Introduction Package from {org_name} to {person_name}\n\n")
            f.write(content)

        end_time = time.time()
        elapsed_time = end_time - start_time

        logger.info(f"Introduction package processed successfully:")
        logger.info(f"Time taken: {elapsed_time:.2f} seconds")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Content length: {len(content)} characters")

        # Additional analysis
        quote_count = content.count('"')  # Rough estimate of quote count
        citation_count = content.count('[')  # Rough estimate of citation count
        logger.info(f"Estimated quote count: {quote_count // 2}")  # Divide by 2 for opening/closing quotes
        logger.info(f"Estimated citation count: {citation_count}")

        return True

    except Exception as e:
        logger.error(f"Error processing introduction package: {str(e)}")
        return False

def main():
    logger.info("Starting the Introduction Letter Generation Process")
    
    PERPLEXITY_API_KEY = load_api_key("RR_LLM_keys.key")

    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

    system_prompts = load_system_prompts()

    organizations_folder = "Organizations"
    research_folder = "People_Research"

    logger.info(f"Processing organizations from: {organizations_folder}")
    logger.info(f"Loading research from: {research_folder}")

    org_count = 0
    person_count = 0
    success_count = 0
    skipped_count = 0

    # Process each organization and research file combination
    for org_folder in os.listdir(organizations_folder):
        org_path = os.path.join(organizations_folder, org_folder)
        if os.path.isdir(org_path):
            org_content, org_line_count = load_organization_file(org_path)
            if not org_content:
                continue
            org_count += 1

            research_files = glob.glob(os.path.join(research_folder, "*_research_*.md"))
            logger.info(f"Found {len(research_files)} research files in {research_folder}")

            for research_file in research_files:
                person_name = os.path.basename(research_file).split("_research")[0].replace("_", " ").title()
                logger.info(f"Processing research for: {person_name}")
                
                with open(research_file, 'r') as f:
                    research_content = f.read()
                person_count += 1

                result = process_introduction_package(client, system_prompts, org_content, research_content, person_name, org_folder, org_line_count)
                if result:
                    success_count += 1
                else:
                    skipped_count += 1

    logger.info("\nProcess Complete:")
    logger.info(f"Organizations processed: {org_count}")
    logger.info(f"People processed: {person_count}")
    logger.info(f"Successful introductions generated: {success_count}")
    logger.info(f"Skipped (already existing) introductions: {skipped_count}")
    logger.info(f"Output folder: Introductions/")

if __name__ == "__main__":
    main()
