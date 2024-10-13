import os
import json
import time
import logging
from openai import OpenAI
from datetime import datetime
import glob

# Set up logging
logging.basicConfig(filename='perplexity_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create Markdown_Output directory if it doesn't exist
output_dir = "Markdown_Output"
os.makedirs(output_dir, exist_ok=True)

YOUR_API_KEY = ""

# Load prompts from Prompts.json
with open("Prompts.json", "r") as f:
    prompts = json.load(f)

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

system_message = {
    "role": "system",
    "content": (
        "You are a comprehensive Myrmecology researcher, specializing in the study of ants. "
        "Your responses should always include exhaustive internet research on the topic at hand. "
        "Provide detailed, academic-level information, citing primary sources with URLs and DOIs whenever possible. "
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
        "\n- [Hyperlinks](URL) for referencing external sources"
        "\n\n"
        "Conclude each response with a comprehensive, APA-formatted bibliography of all sources cited. "
        "Your goal is to provide the most thorough, well-structured, and up-to-date information available on any ant-related query, "
        "presented in a clear and academically rigorous manner."
    ),
}

for prompt_id, prompt_data in prompts.items():
    # Check if a file with the same prompt number and short name already exists
    existing_files = glob.glob(os.path.join(output_dir, f"Prompt_{prompt_id}_{prompt_data['short_name']}*.md"))
    
    if existing_files:
        skip_message = f"Skipping Prompt {prompt_id} ({prompt_data['short_name']}): Output already exists."
        print(skip_message)
        logging.info(skip_message)
        continue

    messages = [
        system_message,
        {
            "role": "user",
            "content": prompt_data["prompt"],
        },
    ]

    # Generate a unique filename based on the prompt number, short name, and current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"Prompt_{prompt_id}_{prompt_data['short_name']}_{timestamp}.md")

    logging.info(f"Processing Prompt {prompt_id}: {prompt_data['prompt'][:50]}...")

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

        print(f"Markdown response for Prompt {prompt_id} saved to {output_file}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Number of lines in output: {line_count}")

    except Exception as e:
        logging.error(f"Error processing Prompt {prompt_id}: {str(e)}")
        print(f"Error processing Prompt {prompt_id}: {str(e)}")

    print("---")  # Separator for readability in console output

logging.info("All prompts processed.")
print("All prompts processed.")
