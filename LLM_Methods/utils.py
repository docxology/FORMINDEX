from config import DEFAULT_CONFIG
import os
import json
import logging
import time
from typing import Any, Dict, List, Tuple
from openai import OpenAI

client = None

def initialize_openai_client(api_key=None):
    global client
    if api_key is None:
        api_key = get_api_key()
    client = OpenAI(api_key=api_key)
    logging.info("OpenAI client initialized successfully")

def load_file(file_path: str) -> str:
    """
    Load the contents of a file.

    Args:
        file_path (str): Path to the file to be loaded.

    Returns:
        str: Contents of the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If there's an error reading the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logging.info(f"File loaded successfully: {file_path}")
        return content
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise

def save_file(content: str, file_path: str) -> None:
    """
    Save content to a file.

    Args:
        content (str): Content to be saved.
        file_path (str): Path where the file should be saved.

    Raises:
        IOError: If there's an error writing to the file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.info(f"File saved successfully: {file_path}")
    except IOError as e:
        logging.error(f"Error writing to file {file_path}: {str(e)}")
        raise

def setup_logging(log_file: str = 'fieldshift2.log', level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging for the application.

    Args:
        log_file (str): Name of the log file. Defaults to 'fieldshift2.log'.
        level (int): Logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger('FieldSHIFT-2')
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def setup_llm(llm_params: Dict[str, Any] = None) -> None:
    """
    Set up the LLM with the provided API key and parameters.

    Args:
        llm_params (Dict[str, Any]): LLM parameters from config.
    """
    if llm_params is None:
        llm_params = DEFAULT_CONFIG['llm_params']
    logging.info("LLM setup with provided API key and parameters")

def generate_llm_response(prompt: str, llm_params: dict) -> tuple:
    """
    Generate a response from the language model.

    Args:
        prompt (str): The input prompt for the language model.
        llm_params (dict): Parameters for the language model.

    Returns:
        tuple: A tuple containing the generated text and the number of tokens used.
    """
    try:
        client = openai.OpenAI(api_key=llm_params['api_key'])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text from English to {llm_params['target_language']}. Maintain the original meaning and style as closely as possible."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip(), response.usage.total_tokens
    except Exception as e:
        raise Exception(f"Error generating LLM response: {str(e)}")

def batch_process_llm(prompts: List[str], llm_params: Dict[str, Any] = DEFAULT_CONFIG['llm_params']) -> List[Tuple[str, float]]:
    """
    Process a batch of prompts through the LLM.

    Args:
        prompts (List[str]): List of input prompts for the LLM.
        llm_params (Dict[str, Any]): LLM parameters from config.

    Returns:
        List[Tuple[str, float]]: List of generated responses from the LLM and their respective processing times.
    """
    responses = []
    for prompt in prompts:
        response, time_taken = generate_llm_response(prompt, llm_params)
        responses.append((response, time_taken))
    logging.info(f"Batch processed {len(prompts)} prompts through LLM")
    return responses

def get_api_key() -> str:
    """
    Read the OpenAI API key from the LLM_keys.key file.

    Returns:
        str: The OpenAI API key.

    Raises:
        ValueError: If the API key is not found in the file.
    """
    key_file_path = os.path.join(os.path.dirname(__file__), 'LLM_keys.key')
    try:
        with open(key_file_path, 'r') as key_file:
            for line in key_file:
                if line.startswith('OPENAI_API_KEY'):
                    api_key = line.split('=')[1].strip()
                    logging.info("API key read successfully")
                    return api_key
    except FileNotFoundError:
        logging.error(f"API key file not found: {key_file_path}")
    except Exception as e:
        logging.error(f"Error reading API key: {str(e)}")

    raise ValueError("OPENAI_API_KEY not found in LLM_keys.key file")

def extract_entity_files(base_dir: str) -> List[str]:
    """
    Extract entity .py files from the Inputs_and_Outputs/Entity/ subfolders.

    Args:
        base_dir (str): The base directory to start the search.

    Returns:
        List[str]: List of paths to the entity .py files.
    """
    entity_files = []
    entity_dir = os.path.join(base_dir, 'Inputs_and_Outputs', 'Entity')

    logging.info(f"Searching for entity files in directory: {entity_dir}")

    for root, _, files in os.walk(entity_dir):
        logging.info(f"Checking directory: {root}")
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                entity_files.append(file_path)
                logging.info(f"Found entity file: {file_path}")

    logging.info(f"Total entity files found: {len(entity_files)}")
    return entity_files

def extract_organization_files(base_dir: str) -> List[str]:
    """
    Extract organization .py files from the Inputs_and_Outputs/Organization/ subfolders.

    Args:
        base_dir (str): The base directory to start the search.

    Returns:
        List[str]: List of paths to the organization .py files.
    """
    organization_files = []
    organization_dir = os.path.join(base_dir, 'Inputs_and_Outputs', 'Organization')

    logging.info(f"Searching for organization files in directory: {organization_dir}")

    for root, _, files in os.walk(organization_dir):
        logging.info(f"Checking directory: {root}")
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                organization_files.append(file_path)
                logging.info(f"Found organization file: {file_path}")

    logging.info(f"Total organization files found: {len(organization_files)}")
    return organization_files