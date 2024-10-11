import logging
import os
import openai
from utils import load_file, save_file, generate_llm_response, get_api_key
from config import USER_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the input directory and output directory
base_dir = "/home/trim/Documents/GitHub/GEN24 /GEN-24/"
INPUT_DIR = os.path.join(base_dir, "Inputs_and_Outputs", "Written_Introduction_Letter")
OUTPUT_DIR = os.path.join(base_dir, "Inputs_and_Outputs", "Translated_Letters")

# Define target languages
TARGET_LANGUAGES = [
    'English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Russian', 'Portuguese', 'Arabic',
    'Hindi', 'Bengali', 'Punjabi', 'Korean', 'Turkish', 'Vietnamese', 'Italian', 'Thai', 'Gujarati', 'Malay'
]

def process_introduction_letter(input_file: str, output_dir: str, llm_params: dict, language: str) -> None:
    """
    Process an introduction letter file, send it to LLM for translation, and save the response as markdown.

    Args:
        input_file (str): Path to the input introduction letter file.
        output_dir (str): Directory to save the translated letter.
        llm_params (dict): Parameters for the language model.
        language (str): Target language for translation.
    """
    try:
        logger.info(f"Processing file: {input_file} for translation to {language}")

        # Load letter content
        letter_content = load_file(input_file)

        # Prepare the content for LLM
        llm_input = f"Your job is to translate this faithfully into {language}. The content is:\n{letter_content}"

        # Generate the translated letter using LLM
        llm_params['target_language'] = language
        translated_letter, _ = generate_llm_response(llm_input, llm_params)

        # Prepare the output file path
        output_file_name = f'translated_{language}_' + os.path.splitext(os.path.basename(input_file))[0] + '.md'
        language_specific_output_dir = os.path.join(output_dir, language)
        output_file_path = os.path.join(language_specific_output_dir, output_file_name)

        # Ensure the language-specific output directory exists
        os.makedirs(language_specific_output_dir, exist_ok=True)

        # Save the translated letter as markdown
        save_file(translated_letter, output_file_path)

        logger.info(f"Translated letter saved as markdown: {output_file_path}")
    except Exception as e:
        logger.error(f"Error processing file {input_file} for translation to {language}: {str(e)}")

def process_introduction_letters(input_dir: str, output_dir: str, config: dict) -> None:
    try:
        logger.info("Starting introduction letter processing")

        # Get the API key using the get_api_key() function
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key not found in .env or LLM_keys.key file")

        # Prepare LLM parameters
        llm_params = {**USER_CONFIG['llm_params'], 'api_key': api_key}

        # Ensure the output directory exists and is writable
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Permission denied: '{output_dir}'")

        # Process each markdown file in the input directory
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.md'):
                input_file = os.path.join(input_dir, file_name)
                logger.info(f"Found input file: {input_file}")
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"Successfully read {len(content)} characters from the input file")
                
                for language in TARGET_LANGUAGES:
                    process_introduction_letter(input_file, output_dir, llm_params, language)

        logger.info("Introduction letter processing completed successfully.")
    except Exception as e:
        logger.error(f"Error in process_introduction_letters: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting script execution")

    # Define the base directory for configuration
    base_dir = "/home/trim/Documents/Github/GEN24 /GEN-24/"

    # Create a configuration dictionary
    config = {
        'base_dir': base_dir,
        'languages': TARGET_LANGUAGES,
        'output_dirs': {
            'Translated_Letters': OUTPUT_DIR
        }
    }

    # Process the introduction letters in the input directory
    process_introduction_letters(INPUT_DIR, OUTPUT_DIR, config)

    logger.info("Script execution completed")