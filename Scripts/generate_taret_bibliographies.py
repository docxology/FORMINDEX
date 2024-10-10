import json
import os
from collections import defaultdict

# List of target bibliographies
TARGET_BIBLIOGRAPHIES = [
    "Formica", "Camponotus", "Myrmica", "Pheidole", "Monomorium", "Messor", "Cataglyphis",
    "Foraging", "Bioenergetics", "Myrmecophiles", "Ant-plant symbioses",
    "Hawaii", "India", "Mexico", "Brazil"
]

def load_formis_data(file_path):
    """Load FORMIS data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please ensure the file exists and the path is correct.")
        return None

def extract_terms(entry):
    """Extract all target terms mentioned in any field of the entry."""
    terms = set()
    for value in entry.values():
        if isinstance(value, str):
            for term in TARGET_BIBLIOGRAPHIES:
                if term.lower() in value.lower():
                    terms.add(term)
    return terms

def generate_targeted_bibliographies(formis_data):
    """Generate bibliographies for target terms."""
    targeted_bibliographies = defaultdict(list)
    
    for entry in formis_data:
        terms = extract_terms(entry)
        for term in terms:
            targeted_bibliographies[term].append(entry)
    
    return targeted_bibliographies

def save_targeted_bibliographies(targeted_bibliographies, output_dir):
    """Save targeted bibliographies as JSON files in separate folders."""
    for term, bibliography in targeted_bibliographies.items():
        term_dir = os.path.join(output_dir, term)
        os.makedirs(term_dir, exist_ok=True)
        
        output_file = os.path.join(term_dir, f"{term}_bibliography.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bibliography, f, ensure_ascii=False, indent=2)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_file = os.path.join(project_root, "Initial_Files", "FORMIS_2024_July_Bibtex.json")
    output_dir = os.path.join(project_root, "Targeted_Bibliographies")
    
    # Load FORMIS data
    formis_data = load_formis_data(input_file)
    if formis_data is None:
        return
    
    # Generate targeted bibliographies
    targeted_bibliographies = generate_targeted_bibliographies(formis_data)
    
    # Save targeted bibliographies
    save_targeted_bibliographies(targeted_bibliographies, output_dir)
    
    print(f"Generated {len(targeted_bibliographies)} targeted bibliographies.")
    for term, bibliography in targeted_bibliographies.items():
        print(f"  - {term}: {len(bibliography)} entries")

if __name__ == "__main__":
    main()