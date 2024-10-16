import os
import json
import time
from openai import OpenAI
from datetime import datetime
import glob
import logging
import itertools

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger = logging.getLogger('')
    logger.handlers = [console_handler]
    return logger

logger = setup_logging()

# Specify target System and User prompts by short name

TARGET_SYSTEM_PROMPTS = [
   "innovators_catechism_pitch",
   "local_journalist",
   "complex_systems_scientist",
   "enthusiastic_undergraduate",
   "data_science_virtuoso",
   "systems_architect",
   "quantum_computing_specialist",
   "futurist_strategist"
]

TARGET_USER_PROMPTS = [
    "active_inference_ant_behavior",
    "active_inference_ants_phd_proposal",
    "active_inference_ant_foraging_simulation",
    "active_inference_events",
    "active_inference_pomdp_python_guide",
    "bayesian_mechanics_fep_quantum_active_inference",
    "rxinfer_julia_summary",
    "whos_on_first_current_events",
    "safe_ose_grant_proposal",
    "northern_california_fire_risk",
    "new_mexico_fire_risk",
    "lake_county_ca_fire_risk"
]

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

def load_prompts():
    user_prompts = load_json_file("User_Prompts.json")
    system_prompts = load_json_file("System_Prompts.json")
    return user_prompts, system_prompts

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

# Function to get user prompt based on short_name
def get_user_prompt(user_prompts, short_name):
    return next((prompt for prompt in user_prompts.values() if prompt["short_name"] == short_name), None)

def process_prompt_combination(client, system_prompts, system_short_name, user_short_name, system_prompt, user_prompt, system_folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(system_folder, f"Prompt_S{system_prompt['number']}_{system_short_name}_U_{user_short_name}_{timestamp}.md")

    existing_files = glob.glob(os.path.join(system_folder, f"Prompt_S{system_prompt['number']}_{system_short_name}_U_{user_short_name}*.md"))
    
    if existing_files:
        logger.info(f"Skipping combination (System: {system_short_name}, User: {user_short_name}): Output already exists.")
        return

    messages = [
        get_system_message(system_prompts, system_short_name),
        {
            "role": "user",
            "content": user_prompt["prompt"],
        },
    ]

    logger.info(f"\nProcessing Prompt Combination:")
    logger.info(f"System Prompt: {system_short_name}")
    logger.info(f"User Prompt: {user_short_name}")
    logger.info(f"Full User Prompt: {user_prompt['prompt'][:100]}...")
    logger.info(f"System Prompt Content: {messages[0]['content'][:100]}...")  # Log the first 100 characters of system prompt

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

        logger.info(f"Prompt combination processed successfully.")
        logger.info(f"Time taken: {elapsed_time:.2f} seconds")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Number of lines in output: {line_count}")

    except Exception as e:
        logger.error(f"Error processing prompt combination: {str(e)}")

    logger.info("---")
    time.sleep(1)

def main():
    base_output_dir = "Markdown_Output"
    os.makedirs(base_output_dir, exist_ok=True)

    key_file_path = os.path.join('..', 'Perplexity_Methods', 'LLM_keys.key')
    PERPLEXITY_API_KEY = load_api_key(key_file_path)

    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

    user_prompts, system_prompts = load_prompts()

    prompt_combinations = list(itertools.product(TARGET_SYSTEM_PROMPTS, TARGET_USER_PROMPTS))

    for system_short_name, user_short_name in prompt_combinations:
        system_prompt = next((prompt for prompt in system_prompts.values() if prompt["short_name"] == system_short_name), None)
        user_prompt = get_user_prompt(user_prompts, user_short_name)

        if not system_prompt:
            logger.warning(f"System prompt '{system_short_name}' not found. Skipping.")
            continue

        if not user_prompt:
            logger.warning(f"User prompt '{user_short_name}' not found. Skipping.")
            continue

        system_folder = os.path.join(base_output_dir, system_short_name)
        os.makedirs(system_folder, exist_ok=True)

        process_prompt_combination(client, system_prompts, system_short_name, user_short_name, system_prompt, user_prompt, system_folder)

    logger.info("All prompt combinations processed.")

if __name__ == "__main__":
    main()
