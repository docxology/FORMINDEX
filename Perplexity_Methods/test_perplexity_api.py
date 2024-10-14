import os
import time
import logging
from openai import OpenAI
from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the API key
key_file_path = os.path.join('..', 'LLM_Methods', 'LLM_keys.key')
try:
    with open(key_file_path, 'r') as key_file:
        API_KEY = key_file.read().strip()
except FileNotFoundError:
    logger.error(f"API key file not found at {key_file_path}")
    raise

# Initialize the client
client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")

# Test message
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, can you hear me?"}
]

def make_api_request(retries=3, delay=5):
    """
    Make an API request with retry logic.
    
    :param retries: Number of retry attempts
    :param delay: Delay between retries in seconds
    :return: API response or None if all attempts fail
    """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-sonar-large-128k-online",
                messages=messages,
            )
            logger.info("API request successful")
            return response
        except ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
        except Timeout as e:
            logger.warning(f"Request timed out on attempt {attempt + 1}: {e}")
        except HTTPError as e:
            logger.error(f"HTTP error on attempt {attempt + 1}: {e.response.status_code} - {e.response.reason}")
            if e.response.status_code >= 500:  # Server error, worth retrying
                logger.info(f"Retrying due to server error (attempt {attempt + 1})")
            else:
                logger.error("Client error, not retrying")
                return None
        except RequestException as e:
            logger.error(f"Request exception on attempt {attempt + 1}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
        
        if attempt < retries - 1:
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    logger.error("All retry attempts failed")
    return None

def main():
    response = make_api_request()
    if response:
        print("API Response:")
        print(response.choices[0].message.content)
    else:
        print("Failed to get a response from the API after multiple attempts")

if __name__ == "__main__":
    main()
