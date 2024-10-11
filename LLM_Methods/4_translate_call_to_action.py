import logging
import os
import openai
from utils import load_file, save_file, generate_llm_response, get_api_key
from config import USER_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define target languages
TARGET_LANGUAGES = [
    'English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Russian', 'Portuguese', 'Arabic',
    'Hindi', 'Bengali', 'Punjabi', 'Korean', 'Turkish', 'Vietnamese', 'Italian', 'Thai', 'Gujarati', 'Malay',
    'Swahili', 'Indonesian', 'Urdu', 'Dutch', 'Polish', 'Swedish', 'Greek', 'Romanian', 'Czech', 'Tagalog'
]

# Define target audiences
TARGET_AUDIENCES = [
    'Systems Change Funders',
    'Textile Factory Workers',
    'Fashion Models',
    'Fashion Designers',
    'Sustainable Fashion Entrepreneurs',
    'Fashion Journalists',
    'Textile Recycling Companies',
    'Fashion Students',
    'Garment Industry Executives',
    'Ethical Fashion Influencers',
    'Textile Engineers'
]

def process_call_to_action(output_dir: str, llm_params: dict, language: str, audience: str) -> None:
    try:
        logger.info(f"Processing translation to {language} for audience {audience}")

        # Update the content preparation for LLM
        llm_input = f"""
Translate and adapt the following call to action into {language}, specifically tailored for {audience}. 

Crucial instructions:
1. Begin the letter by directly addressing {audience} and highlighting their importance to this initiative.
2. Throughout the content, infuse {audience}'s specific concerns, skills, and unique position in the fashion industry.
3. Adapt examples, statistics, and impacts to be most relevant and compelling to {audience}.
4. Use language, tone, and framing that will resonate deeply with {audience} in their cultural and professional context.
5. Maintain the original structure, including headings and paragraphs, but feel free to adjust content within each section to better speak to {audience}.
6. Ensure that all core messages are preserved while making them highly relevant and actionable for {audience}.

Here's the content to translate and adapt:

---

Join the ReclAIME'd/Waste to Energy Campaign: A Call to Action for Change!

Background:

The global textile and fashion industry presents a profound challenge to our environment and human well-being. With a market size that reached approximately $987.95 billion as of 2023—projected to expand to nearly $1.35 trillion by 2032—the industry stands at a crossroads. The urgent need for sustainable practices has never been clearer. The 2024 report from McKinsey & Company, Global Fashion Agenda, and the UN Alliance for Sustainable Fashion starkly outlines the consequences of inaction: extreme climate events are jeopardizing the lives and livelihoods of fashion workers, threatening an estimated $65 billion in apparel exports by 2030.

The challenges we face include:

Environmental Impact: The fashion industry depletes resources, pollutes, and generates waste.
Human Rights Concerns: Labor exploitation, poor working conditions, and human rights violations are pervasive issues.
Lack of Transparency: Greenwashing and insufficient data hinder informed consumer choices and assessments of company sustainability.
In response to these pressing challenges, we invite you to be a part of the solution. The ReclAIME'd Fashion System Micro-economy aims to leverage shifting consumer preferences and trends, transforming fashion from a superficial industry into a powerful tool for communication, social change, and democracy. It is time to harness the industry's potential to create economic incentives that benefit both the environment and society.

Introducing the 100 Trashion Club:

We are calling upon fashion designers, agencies, event promoters, and all relevant stakeholders to join our 100 Trashion Club. This initiative will collaborate on innovative solutions to tackle global waste management issues. 

The Shebang Trashion Show, organized by the BUNTU WELLBEING EXPERIENCE NETWORK, showcases the stories behind the garments, emphasizing fashion's role in addressing climate change. This event elevates fashion from mere aesthetics to a powerful form of expression, celebrating journeys of resistance and resilience. Our first Trashion Show, held on July 20, 2024, highlighted the community impact of waste, illustrating how the fashion world can advocate for change.

Consider this urgent situation: just three weeks after our last Trashion Show, a landfill located a mere 20 kilometers away resulted in a tragic loss of over 40 lives. The time to act is now, and we need your voice. 

Your Role:

Join us in organizing a Trashion Runway that delivers a powerful message about waste management and the vital contribution of the fashion and arts community to this pressing issue. According to recent reports from the IPC, we are running out of time. Together, we can influence change and promote sustainable practices in the fashion industry.

Take Action:

The ball is in your court! Join us in the 100 Trashion Club. Together, we can create solutions that matter and transform our approach to fashion and waste. Let's use our creativity and passion to drive change and ignite conversations that lead to real, tangible progress.

---

Now provide the complete translated and adapted version of the call to action in {language}, tailored for {audience}.
Remember to start by directly addressing {audience} and to weave their perspective throughout the entire letter.
Ensure you've transformed the content to truly speak to {audience}'s concerns, motivations, skills, and cultural context.
Do not include any additional explanations or notes. Only return the translated and adapted text.
"""

        # Generate the translated call to action using LLM
        translated_content, _ = generate_llm_response(llm_input, llm_params)

        if not translated_content or translated_content.strip().startswith("I'm sorry"):
            raise ValueError(f"Failed to generate proper translation for {language} and {audience}")

        # Prepare the output file path
        output_file_name = f'translated_{language}_{audience}_ReclAIMEd_Call_To_Action.md'
        language_specific_output_dir = os.path.join(output_dir, language)
        output_file_path = os.path.join(language_specific_output_dir, output_file_name)

        # Ensure the language-specific output directory exists
        os.makedirs(language_specific_output_dir, exist_ok=True)

        # Save the translated content as markdown
        save_file(translated_content, output_file_path)

        logger.info(f"Translated call to action saved as markdown: {output_file_path}")
    except Exception as e:
        logger.error(f"Error processing translation to {language} for audience {audience}: {str(e)}")

def process_call_to_actions(output_dir: str, config: dict) -> None:
    try:
        logger.info("Starting call to action processing")

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

        for language in TARGET_LANGUAGES:
            for audience in TARGET_AUDIENCES:
                process_call_to_action(output_dir, llm_params, language, audience)

        logger.info("Call to action processing completed successfully.")
    except Exception as e:
        logger.error(f"Error in process_call_to_actions: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting script execution")

    # Correct base_dir path that has the space after GEN24 space
    base_dir = "/home/trim/Documents/GitHub/GEN24 /GEN-24/"

    # Create a configuration dictionary
    config = {
        'base_dir': base_dir,
        'languages': TARGET_LANGUAGES,
        'audiences': TARGET_AUDIENCES,
        'output_dirs': {
            'Call_to_Action': os.path.join(base_dir, "Inputs_and_Outputs", "Call_to_Action")
        }
    }

    # Process the call to action
    process_call_to_actions(config['output_dirs']['Call_to_Action'], config)

    logger.info("Script execution completed")