import os
import json
import time
from openai import OpenAI
from datetime import datetime
import glob
import logging

# Set up logging to console only
logging.basicConfig(level=logging.INFO, format='%(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger('').addHandler(console_handler)

# Create Markdown_Output directory if it doesn't exist
output_dir = "Markdown_Output"
os.makedirs(output_dir, exist_ok=True)

key_file_path = os.path.join('..', 'Perplexity_Methods', 'LLM_keys.key')
try:
    with open(key_file_path, 'r') as key_file:
        keys = key_file.read().strip().split('\n')
        logging.info(f"Contents of key file: {keys}")  # Log the contents of the file
        api_keys = dict(key.split('=') for key in keys)
        PERPLEXITY_API_KEY = api_keys.get('PERPLEXITY_API_KEY')
    
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not found in the key file")
    
    logging.info(f"Perplexity API Key: {PERPLEXITY_API_KEY[:5]}...{PERPLEXITY_API_KEY[-5:]}")  # Log the first and last 5 characters of the API key
except FileNotFoundError:
    logging.error(f"API key file not found at {key_file_path}")
    raise
except Exception as e:
    logging.error(f"Error reading API key: {str(e)}")
    raise

# Initialize the client
client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

# Load prompts from Prompts.json
try:
    with open("Prompts.json", "r") as f:
        prompts = json.load(f)
except FileNotFoundError:
    logging.error("Prompts.json file not found")
    raise
except json.JSONDecodeError:
    logging.error("Error decoding Prompts.json file")
    raise

system_message = {
    "role": "system",
    "content": (
        "You are a comprehensive Myrmecology researcher, specializing in the study of ants. "
        "Your responses should always include exhaustive internet research on the topic at hand. "
        "Provide detailed, academic-level information, citing primary sources using PLOS citation format [1] or [2-5]. "
        "Your answers should reflect the latest scientific findings in the field of Myrmecology. "
        "Always strive to present a balanced view of current research, highlighting areas of consensus "
        "as well as ongoing debates or uncertainties in the field. Include relevant statistical data, "
        "methodologies, and experimental results when appropriate. "
        "\n\n"
        "Ensure your responses are thoughtful, full-length, and comprehensive, covering all aspects of the query in depth. "
        "Use proper Markdown formatting throughout your response, including:"
        "\n- Headers and subheaders (##, ###) for clear structure"
        "\n- Bullet points and numbered lists for organized information"
        "\n- **Bold** and *italic* text for emphasis"
        "\n- `Code blocks` for any scientific names, chemical formulas, or code snippets"
        "\n- > Blockquotes for important quotes or key points"
        "\n- Tables for presenting data or comparisons"
        "\n\n"
        "Conclude each response with a comprehensive, numbered plaintext bibliography of all sources cited. "
        "Each entry in the bibliography should include:"
        "\n1. Authors (Last name, First initial.)"
        "\n2. Year of publication"
        "\n3. Title of the article or book chapter"
        "\n4. Journal name (if applicable)"
        "\n5. Volume and issue number (if applicable)"
        "\n6. Page numbers or article number"
        "\n7. DOI (if available)"
        "\n8. URL (if available)"
        "\n\nExample bibliography entry:"
        "\n1. Smith J, Doe A. 2023. Recent advances in ant colony behavior. Journal of Myrmecology. 45(2): 123-145. DOI: 10.1234/jmyrm.2023.45.2.123. https://example.com/article"
        "\n\n"
        "Your goal is to provide the most thorough, well-structured, and up-to-date information available on any ant-related query, "
        "presented in a clear and academically rigorous manner with proper citations and a complete bibliography."
    ),
}

for prompt_id, prompt_data in prompts.items():
    # Check if a file with the same prompt number and short name already exists
    existing_files = glob.glob(os.path.join(output_dir, f"Prompt_{prompt_id}_{prompt_data['short_name']}*.md"))
    
    if existing_files:
        logging.info(f"Skipping Prompt {prompt_id} ({prompt_data['short_name']}): Output already exists.")
        continue

    messages = [
        system_message,
        {
            "role": "user",
            "content": prompt_data["prompt"],
        },
    ]

    logging.info(f"\nProcessing Prompt {prompt_id}:")
    logging.info(f"Full Prompt: {prompt_data['prompt'][:100]}...")

    # Generate a unique filename based on the prompt number, short name, and current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"Prompt_{prompt_id}_{prompt_data['short_name']}_{timestamp}.md")

    # Measure the time taken for the API request
    start_time = time.time()

    # Chat completion and save as Markdown
    try:
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=messages,
        )

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

        logging.info(f"Prompt {prompt_id} processed successfully.")
        logging.info(f"Time taken: {elapsed_time:.2f} seconds")
        logging.info(f"Output file: {output_file}")
        logging.info(f"Number of lines in output: {line_count}")

    except Exception as e:
        logging.error(f"Error processing Prompt {prompt_id}: {str(e)}")

    logging.info("---")  # Add a separator between prompts
    time.sleep(1)  # Wait for 1 second between requests

logging.info("All prompts processed.")
