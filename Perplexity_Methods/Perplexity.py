import os
import json
import time
from openai import OpenAI
from datetime import datetime
import glob
import logging
import itertools

# Set up logging to console only
logging.basicConfig(level=logging.INFO, format='%(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger = logging.getLogger('')
logger.handlers = [console_handler]  # Remove default handlers and add only console handler

# Specify target System and User prompts by short name
TARGET_SYSTEM_PROMPTS = ["comprehensive_myrmecology", "expert_programmer", "local_journalist"]
TARGET_USER_PROMPTS = [
    "uc_davis_ant_research_news",
    "ant_symbolism_spirituality",
    "ant_wisdom_human_applications",
    "ants_in_contemporary_art",
    "ants_indigenous_wisdom_stewardship",
    "active_inference_theoretical_foundations",
    "active_inference_recent_developments",
    "active_inference_ant_behavior",
    "active_inference_ants_phd_proposal",
    "active_inference_ant_foraging_simulation",
    "active_inference_events"
]

# Create base output directory
base_output_dir = "Markdown_Output"
os.makedirs(base_output_dir, exist_ok=True)

key_file_path = os.path.join('..', 'Perplexity_Methods', 'LLM_keys.key')
try:
    with open(key_file_path, 'r') as key_file:
        keys = key_file.read().strip().split('\n')
        api_keys = dict(key.split('=') for key in keys)
        PERPLEXITY_API_KEY = api_keys.get('PERPLEXITY_API_KEY')
    
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not found in the key file")
    
    logging.info("Perplexity API Key loaded successfully")
except FileNotFoundError:
    logging.error(f"API key file not found at {key_file_path}")
    raise
except Exception as e:
    logging.error(f"Error reading API key: {str(e)}")
    raise

# Initialize the client
client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

# Load user prompts from User_Prompts.json
try:
    with open("User_Prompts.json", "r") as f:
        user_prompts = json.load(f)
except FileNotFoundError:
    logging.error("User_Prompts.json file not found")
    raise
except json.JSONDecodeError:
    logging.error("Error decoding User_Prompts.json file")
    raise

# Load system prompts from System_Prompts.json
try:
    with open("System_Prompts.json", "r") as f:
        system_prompts = json.load(f)
except FileNotFoundError:
    logging.error("System_Prompts.json file not found")
    raise
except json.JSONDecodeError:
    logging.error("Error decoding System_Prompts.json file")
    raise

# Function to get system message based on short_name
def get_system_message(short_name):
    system_prompt = next((prompt for prompt in system_prompts.values() if prompt["short_name"] == short_name), None)
    if not system_prompt:
        logging.warning(f"System prompt with short_name '{short_name}' not found. Using default.")
        system_prompt = system_prompts["default"]
    return {
        "role": "system",
        "content": system_prompt["description"]
    }

# Function to get user prompt based on short_name
def get_user_prompt(short_name):
    return next((prompt for prompt in user_prompts.values() if prompt["short_name"] == short_name), None)

# Generate all combinations of target system and user prompts
prompt_combinations = list(itertools.product(TARGET_SYSTEM_PROMPTS, TARGET_USER_PROMPTS))

for system_short_name, user_short_name in prompt_combinations:
    system_prompt = next((prompt for prompt in system_prompts.values() if prompt["short_name"] == system_short_name), None)
    user_prompt = get_user_prompt(user_short_name)

    if not system_prompt:
        logging.warning(f"System prompt '{system_short_name}' not found. Skipping.")
        continue

    if not user_prompt:
        logging.warning(f"User prompt '{user_short_name}' not found. Skipping.")
        continue

    # Create nested folder for the system prompt
    system_folder = os.path.join(base_output_dir, system_short_name)
    os.makedirs(system_folder, exist_ok=True)

    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(system_folder, f"Prompt_S{system_prompt['number']}_{system_short_name}_U_{user_short_name}_{timestamp}.md")

    # Check if a similar file already exists in the system folder
    existing_files = glob.glob(os.path.join(system_folder, f"Prompt_S{system_prompt['number']}_{system_short_name}_U_{user_short_name}*.md"))
    
    if existing_files:
        logging.info(f"Skipping combination (System: {system_short_name}, User: {user_short_name}): Output already exists.")
        continue

    messages = [
        get_system_message(system_short_name),
        {
            "role": "user",
            "content": user_prompt["prompt"],
        },
    ]

    logging.info(f"\nProcessing Prompt Combination:")
    logging.info(f"System Prompt: {system_short_name}")
    logging.info(f"User Prompt: {user_short_name}")
    logging.info(f"Full User Prompt: {user_prompt['prompt'][:100]}...")

    # Measure the time taken for the API request
    start_time = time.time()

    # Chat completion and save as Markdown
    try:
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=messages,
        )
        # Some other Perplexity models, October 16 2024: https://docs.perplexity.ai/guides/model-cards 
                # llama-3.1-sonar-small-128k-online	                
                # llama-3.1-sonar-large-128k-online	
                # llama-3.1-sonar-huge-128k-online	
                # llama-3.1-sonar-small-128k-chat	
                # llama-3.1-sonar-large-128k-chat	
        
        # Extract the content from the response
        content = response.choices[0].message.content

        # Write the content to a Markdown file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Count the number of lines in the output file
        with open(output_file, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)

        logging.info(f"Prompt combination processed successfully.")
        logging.info(f"Time taken: {elapsed_time:.2f} seconds")
        logging.info(f"Output file: {output_file}")
        logging.info(f"Number of lines in output: {line_count}")

    except Exception as e:
        logging.error(f"Error processing prompt combination: {str(e)}")

    logging.info("---")  # Add a separator between prompts
    time.sleep(1)  # Wait for 1 second between requests

logging.info("All prompt combinations processed.")
