import sys
import subprocess
import venv
import os
from openai import OpenAI

def create_venv_if_needed():
    venv_path = os.path.join(os.path.dirname(__file__), 'venv')
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
    
    # Activate the virtual environment
    venv_python = os.path.join(venv_path, 'bin', 'python')
    
    # Update sys.path to include the virtual environment's site-packages
    site_packages = subprocess.check_output([venv_python, '-c', 
        'import site; print(site.getsitepackages()[0])']).decode().strip()
    sys.path.insert(0, site_packages)
    
    # Update sys.prefix to point to the virtual environment
    sys.prefix = venv_path
    
    # Install required packages
    subprocess.check_call([venv_python, "-m", "pip", "install", "openai"])

    # Set the VIRTUAL_ENV environment variable
    os.environ['VIRTUAL_ENV'] = venv_path

    # Modify PATH to prioritize the virtual environment's bin directory
    os.environ['PATH'] = os.path.join(venv_path, 'bin') + os.pathsep + os.environ['PATH']

# Call this function at the beginning of your script
create_venv_if_needed()

import logging
import os
from utils import load_file, save_file, get_api_key
from config import USER_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the input directory and output directory
INPUT_DIR = os.path.join(base_dir, "LLM_Methods", "Inputs_and_Outputs", "LLM_Written_Summary")
OUTPUT_DIR = os.path.join(base_dir, "LLM_Methods", "Inputs_and_Outputs", "Translated_Summaries")

# Define target languages
TARGET_LANGUAGES = [
    'English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Russian', 'Portuguese', 'Arabic',
    'Hindi', 'Bengali', 'Punjabi', 'Korean', 'Turkish', 'Vietnamese', 'Italian', 'Thai', 'Gujarati', 'Malay'
]

def split_text(text, max_chunk_size=3000):
    """Split text into chunks of maximum size."""
    return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

def process_literature_summary(input_file: str, output_dir: str, client: OpenAI, language: str) -> None:
    """
    Process a literature summary file, send it to LLM for translation, and save the response as markdown.

    Args:
        input_file (str): Path to the input literature summary file.
        output_dir (str): Directory to save the translated summary.
        client (OpenAI): OpenAI client instance.
        language (str): Target language for translation.
    """
    try:
        logger.info(f"Processing file: {input_file} for translation to {language}")

        # Load summary content
        summary_content = load_file(input_file)

        # Split the content into smaller chunks
        chunks = split_text(summary_content)
        translated_chunks = []

        for i, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {i+1}/{len(chunks)} for {language}")
            
            # Prepare the content for LLM
            prompt = f"Translate the following text from English to {language}. Maintain the original meaning and style:\n\n{chunk}"

            try:
                response = client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    **{k: v for k, v in USER_CONFIG['llm_params'].items() if k not in ['model', 'api_key', 'max_tokens']}
                )
                translated_chunks.append(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Error translating chunk {i+1} for {language}: {str(e)}")
                translated_chunks.append(chunk)  # Append original chunk if translation fails

        # Combine translated chunks
        translated_summary = "\n".join(translated_chunks)

        # Prepare the output file path
        output_file_name = f'translated_{language}_' + os.path.basename(input_file)
        language_specific_output_dir = os.path.join(output_dir, language)
        output_file_path = os.path.join(language_specific_output_dir, output_file_name)

        # Ensure the language-specific output directory exists
        os.makedirs(language_specific_output_dir, exist_ok=True)

        # Save the translated summary as markdown
        save_file(translated_summary, output_file_path)

        logger.info(f"Translated summary saved as markdown: {output_file_path}")
    except Exception as e:
        logger.error(f"Error processing file {input_file} for translation to {language}: {str(e)}")

def process_literature_summaries(input_dir: str, output_dir: str, config: dict) -> None:
    try:
        logger.info("Starting literature summary processing")

        # Check if the input directory exists
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Get the API key using the get_api_key() function
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key not found in .env or LLM_keys.key file")

        # Create OpenAI client
        client = OpenAI(api_key=api_key)

        # Ensure the output directory exists and is writable
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Permission denied: '{output_dir}'")

        # Process each markdown file in the input directory with the specific naming pattern
        files_processed = 0
        for file_name in os.listdir(input_dir):
            if file_name.endswith('_bibliography_summary.md'):
                input_file = os.path.join(input_dir, file_name)
                logger.info(f"Found input file: {input_file}")
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"Successfully read {len(content)} characters from the input file")
                
                for language in TARGET_LANGUAGES:
                    process_literature_summary(input_file, output_dir, client, language)
                files_processed += 1

        if files_processed == 0:
            logger.warning(f"No *_bibliography_summary.md files found in the input directory: {input_dir}")
        else:
            logger.info(f"Processed {files_processed} files successfully.")

        logger.info("Literature summary processing completed successfully.")
    except Exception as e:
        logger.error(f"Error in process_literature_summaries: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting script execution")
    logger.info(f"Base directory: {base_dir}")
    logger.info(f"Input directory: {INPUT_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")

    # Create a configuration dictionary
    config = {
        'base_dir': base_dir,
        'languages': TARGET_LANGUAGES,
        'output_dirs': {
            'Translated_Summaries': OUTPUT_DIR
        }
    }

    # Process the literature summaries in the input directory
    process_literature_summaries(INPUT_DIR, OUTPUT_DIR, config)

    logger.info("Script execution completed")