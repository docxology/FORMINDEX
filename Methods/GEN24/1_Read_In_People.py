import csv
import json
import os
from collections import Counter

def is_valid_linkedin_url(url):
    return url.strip().lower().startswith('https://') and 'linkedin.com' in url.lower()

def read_and_process_people(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    people_prompts = {}
    field_completeness = Counter()
    unique_values = {}

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Read the header row
            header = next(reader)
            print("CSV columns:", header)

            # Map expected column names to actual column indices
            column_mapping = {
                'Name': 0,
                'Title': 1,
                'Organization': 2,
                'LinkedIn': 3
            }

            # Update unique_values dictionary based on actual columns
            for col in column_mapping.keys():
                unique_values[col] = set()

            total_rows = 0
            
            for index, row in enumerate(reader, start=1):
                total_rows += 1
                # Check if required fields exist and are non-empty
                for field, col_index in column_mapping.items():
                    if col_index < len(row):
                        value = row[col_index].strip()
                        if field == 'LinkedIn':
                            if is_valid_linkedin_url(value):
                                field_completeness[field] += 1
                                unique_values[field].add(value)
                        elif value:
                            field_completeness[field] += 1
                            unique_values[field].add(value)

                name = row[column_mapping['Name']]
                organization = row[column_mapping['Organization']]
                title = row[column_mapping['Title']]

                prompt = f"""You are an elite philanthropic intelligence analyst specializing in ultra-high-net-worth individuals (UHNWIs). Your mission is to conduct exhaustive, meticulous research on {name}, {title} at {organization}, uncovering their deepest motivations, values, and impact preferences related to charitable giving and social impact. Your research must be comprehensive, drawing from a vast array of sources to create a nuanced, multi-dimensional profile.

Follow the Research Methodology, Areas of Investigation, and Analysis Framework outlined in the main system prompt. Focus particularly on:

1. Their philanthropic history and current activities
2. Direct quotes and public statements related to charitable giving and social impact
3. Explicit and implicit preferences for philanthropic engagement
4. Their theory of change and approach to systemic impact
5. Potential alignment with our organization's mission

Provide a detailed report following the Output Structure specified in the main system prompt, ensuring to:

- Use extensive, properly formatted citations for all information
- Prioritize direct quotes from {name}
- Clearly distinguish between explicit statements and implicit preferences
- Incorporate data visualizations and tables where appropriate
- Highlight key insights or potential action items in bold
- Use italics for emphasis on important concepts or findings

Your goal is to create an unparalleled, comprehensive donor intelligence report that provides deep, actionable insights for philanthropic organizations. This report should enable them to develop highly tailored engagement strategies, maximizing the potential for meaningful collaboration and transformative impact with {name}."""

                people_prompts[str(index)] = {
                    "prompt": prompt,
                    "short_name": f"{name.lower().replace(' ', '_')}_research",
                    "full_data": dict(zip(header, row))  # Include all data from the CSV
                }

        # Write to RR_People_Prompts.json
        people_prompts_path = os.path.join(os.path.dirname(file_path), "RR_People_Prompts.json")
        with open(people_prompts_path, 'w', encoding='utf-8') as json_file:
            json.dump(people_prompts, json_file, indent=2)

        print(f"\nSuccessfully processed {len(people_prompts)} people and wrote prompts to RR_People_Prompts.json")
        print(f"\nTotal rows in CSV: {total_rows}")
        print("\nField completeness:")
        for field in column_mapping.keys():
            completeness_percentage = (field_completeness[field] / total_rows) * 100
            print(f"  {field}: {field_completeness[field]} / {total_rows} ({completeness_percentage:.2f}%)")

        print("\nUnique values count:")
        for field in column_mapping.keys():
            print(f"  {field}: {len(unique_values[field])}")

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "RR_People_No_Contact.csv")
    read_and_process_people(file_path)
