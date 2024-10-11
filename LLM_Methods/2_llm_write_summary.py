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
    subprocess.check_call([venv_python, "-m", "pip", "install", "tiktoken"])

    # Set the VIRTUAL_ENV environment variable
    os.environ['VIRTUAL_ENV'] = venv_path

    # Modify PATH to prioritize the virtual environment's bin directory
    os.environ['PATH'] = os.path.join(venv_path, 'bin') + os.pathsep + os.environ['PATH']

# Call this function at the beginning of your script
create_venv_if_needed()

import logging
import os
import time
from utils import load_file, save_file, generate_llm_response, get_api_key
from config import USER_CONFIG, chunk_text
import tiktoken

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the input file and output directory
base_dir = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(base_dir, "Inputs_and_Outputs", "Literature_ProSummary")
OUTPUT_DIR = os.path.join(base_dir, "Inputs_and_Outputs", "LLM_Written_Summary")

print("Current working directory:", os.getcwd())

def process_summary(input_file: str, output_dir: str, llm_params: dict) -> None:
    """
    Process a summary file, send it to LLM, and save the response as markdown.

    Args:
        input_file (str): Path to the input summary file.
        output_dir (str): Directory to save the processed summary.
        llm_params (dict): Parameters for the language model.
    """
    try:
        logger.info(f"Processing file: {input_file}")

        # Load summary content
        summary_content = load_file(input_file)

        # Generate the processed summary using LLM
        processed_summary, _ = generate_llm_response(summary_content, llm_params)

        # Prepare the output file path
        output_file_name = 'written_' + os.path.splitext(os.path.basename(input_file))[0] + '.md'
        output_file_path = os.path.join(output_dir, output_file_name)

        # Save the processed summary as markdown
        save_file(processed_summary, output_file_path)

        logger.info(f"Processed summary saved as markdown: {output_file_name}")
    except Exception as e:
        logger.error(f"Error processing file {input_file}: {str(e)}")

def process_summaries(input_dir: str, output_dir: str, config: dict) -> None:
    """
    Process all summary files in the input directory using the provided configuration.

    Args:
        input_dir (str): Directory containing input summary files.
        output_dir (str): Directory to save the processed summaries.
        config (dict): Configuration dictionary.
    """
    try:
        logger.info("Starting summary processing")

        # Get the API key
        try:
            api_key = get_api_key()
        except Exception as e:
            logger.error(f"Error getting API key: {str(e)}")
            return

        if not api_key:
            logger.error("API key not found. Please set the OPENAI_API_KEY environment variable or add it to the LLM_keys.key file.")
            return

        # Create OpenAI client
        client = OpenAI(api_key=api_key)

        # Prepare LLM parameters
        llm_params = {**USER_CONFIG['llm_params'], 'api_key': api_key}

        # Ensure the input directory exists
        if not os.path.exists(input_dir):
            logger.error(f"Input directory not found: {input_dir}")
            return

        # Ensure the output directory exists and is writable
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            logger.error(f"Permission denied: '{output_dir}'")
            return

        # Process all summary files in the input directory
        summary_files = [f for f in os.listdir(input_dir) if f.endswith('.md')]
        if not summary_files:
            logger.warning(f"No .md files found in the input directory: {input_dir}")
            return

        for filename in summary_files:
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, 'written_' + filename)

            # Check if the output file already exists
            if os.path.exists(output_file):
                logger.info(f"Output file already exists: {output_file}. Skipping LLM request.")
                print(f"Output file already exists: {output_file}. Skipping LLM request.")
            else:
                # Process the summary
                start_time = time.time()
                process_file(input_file, client)  # Changed this line
                elapsed_time = time.time() - start_time
                logger.info(f"Elapsed time for processing {filename}: {elapsed_time:.2f} seconds")

        logger.info("Summary processing completed successfully.")
    except Exception as e:
        logger.error(f"Error in process_summaries: {str(e)}")

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def process_file(file_path: str, client: OpenAI) -> None:
    logger.info(f"Processing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Use cl100k_base encoding for GPT-4 models
        encoding_name = "cl100k_base"
        
        # Adjust max tokens for input (GPT-4-mini has a 8k context window)
        max_input_tokens = 7000  # Leave some room for the response
        
        # Chunk the content
        chunks = chunk_text(content, USER_CONFIG['chunk_size'], USER_CONFIG['overlap'])
        
        summarized_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1} of {len(chunks)}")
            
            prompt = f"Summarize the following text, focusing on the key points and main ideas:\n\n{chunk}"
            
            # Check token count and reduce if necessary
            while num_tokens_from_string(prompt, encoding_name) > max_input_tokens:
                chunk = chunk[:int(len(chunk)*0.9)]  # Reduce chunk size by 10%
                prompt = f"Summarize the following text, focusing on the key points and main ideas:\n\n{chunk}"
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4-0125-preview",  # Use the correct model name for GPT-4-mini
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,  # Adjust based on your needs, but keep it within limits
                    **{k: v for k, v in USER_CONFIG['llm_params'].items() if k not in ['model', 'api_key', 'max_tokens']}
                )
                summarized_chunks.append(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {str(e)}")
        
        # Combine summarized chunks
        combined_summary = "\n\n".join(summarized_chunks)
        
        # Write the combined summary to a file
        output_file_path = os.path.join(USER_CONFIG['output_dirs']['LLM_Written_Summary'], os.path.basename(file_path))
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(combined_summary)
        
        logger.info(f"Summary written to {output_file_path}")
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting script execution")

    # Create a configuration dictionary
    config = {
        'base_dir': base_dir,
        'output_dirs': {
            'LLM_Written_Summary': OUTPUT_DIR
        }
    }

    # Process the summaries
    process_summaries(INPUT_DIR, OUTPUT_DIR, config)

    logger.info("Script execution completed")