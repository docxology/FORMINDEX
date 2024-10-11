import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_api_key():
    key_file_path = os.path.join(os.path.dirname(__file__), 'LLM_keys.key')
    try:
        with open(key_file_path, 'r') as key_file:
            for line in key_file:
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        raise ValueError(f"API key file not found at {key_file_path}")
    except IOError:
        raise ValueError(f"Error reading API key file at {key_file_path}")
    
    raise ValueError("OPENAI_API_KEY not found in the key file")

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure output directories exist
def ensure_directories(dirs: Dict[str, str]):
    """
    Ensures that the specified directories exist.

    Args:
        dirs (Dict[str, str]): Dictionary of directory paths.
    """
    for key, path in dirs.items():
        os.makedirs(path, exist_ok=True)

# User-configurable parameters
USER_CONFIG = {
    'output_dirs': {
        'Literature_ProSummary': os.path.join(SCRIPT_DIR, 'Inputs_and_Outputs', 'Literature_ProSummary'),
        'LLM_Written_Summary': os.path.join(SCRIPT_DIR, 'Inputs_and_Outputs', 'LLM_Written_Summary')
    },
    'llm_params': {
        'model': 'gpt-4o-mini', 
        'max_tokens': 120000,  
        'temperature': 0.5,
        'top_p': 1.0,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        'n': 1,
        'stream': False,
        'stop': None,
        'api_key': read_api_key()  # Read the API key from environment variables
    },
    'chunk_size': 100000,  # Number of tokens per chunk
    'overlap': 1000  # Number of overlapping tokens between chunks
}

# Ensure output directories exist
ensure_directories(USER_CONFIG['output_dirs'])

# Default configuration
DEFAULT_CONFIG = {
    'prompts': {
        'pro_shift': "Generate a pro-shifted domain combining the following domains: {domains}",
        'domain_shift': "Shift the following domain: {domain}",
        'dissertation_outline': "Create a dissertation outline for the following shifted domain: {shifted_domain}",
        'pro_grant': "Prepare a grant proposal for exploring, characterizing, and applying the following shifted domain: {shifted_domain}"
    },
    'llm_params': USER_CONFIG['llm_params'],
    'output_dirs': USER_CONFIG['output_dirs']
}

# Add a new function for text chunking
def chunk_text(text: str, chunk_size: int, overlap: int) -> list:
    """
    Split the input text into chunks of specified size with overlap.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum number of tokens per chunk.
        overlap (int): The number of overlapping tokens between chunks.

    Returns:
        list: A list of text chunks.
    """
    import tiktoken

    # Get the encoding for the specified model
    encoding = tiktoken.encoding_for_model(USER_CONFIG['llm_params']['model'])
    
    # Encode the text into tokens
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    while start < len(tokens):
        # Define the end of the current chunk
        end = start + chunk_size
        
        # If this is not the last chunk, adjust the end to respect word boundaries
        if end < len(tokens):
            # Find the last space within the chunk
            while end > start and tokens[end] != encoding.encode(" ")[0]:
                end -= 1
            if end == start:
                end = start + chunk_size  # If no space found, use the original end

        # Extract the chunk and decode it back to text
        chunk = encoding.decode(tokens[start:end])
        chunks.append(chunk)
        
        # Move the start position for the next chunk, considering overlap
        start = end - overlap

    return chunks