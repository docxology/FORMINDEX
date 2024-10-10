import sys
import os
import venv
import subprocess
import json
import logging

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_and_use_venv():
    venv_dir = os.path.join(script_dir, 'venv')
    
    if not os.path.exists(venv_dir):
        logging.info("Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
    
    # Get path to the venv's Python interpreter
    venv_python = os.path.join(venv_dir, 'bin', 'python')
    
    # Install required packages
    required_packages = ['bibtexparser', 'chardet', 'matplotlib', 'seaborn', 'wordcloud', 'scikit-learn', 'numpy']
    for package in required_packages:
        logging.info(f"Installing {package}...")
        subprocess.check_call([venv_python, '-m', 'pip', 'install', package])
    
    logging.info("Virtual environment set up and packages installed.")
    
    return venv_python

def main(venv_python):
    # Import the necessary functions from FORMINDEX_Methods
    sys.path.append(parent_dir)
    from Methods.FORMINDEX_Methods import load_bibtex, export_to_json
    
    # Load BibTeX records
    bibtex_file = os.path.join(parent_dir, 'Initial_Files', 'FORMIS 2024(July)-Bibtex.txt')
    logging.info(f"Attempting to load BibTeX file: {bibtex_file}")
    bibtex_records = load_bibtex(bibtex_file)
    logging.info(f"Loaded {len(bibtex_records)} BibTeX records.")
    
    # Count each @ resource
    resource_counts = {}
    for record in bibtex_records:
        ref_type = record.get('ref_type', 'unknown')
        resource_counts[ref_type] = resource_counts.get(ref_type, 0) + 1

    logging.info("BibTeX resource counts:")
    for ref_type, count in resource_counts.items():
        logging.info(f"{ref_type}: {count}")
    
    # Print the first few records for verification
    logging.info("\nFirst few records:")
    for i, record in enumerate(bibtex_records[:3]):  # Print first 3 records
        logging.info(f"Record {i+1}:")
        for key, value in record.items():
            logging.info(f"  {key}: {value}")
        logging.info("")

    # Export to JSON
    json_file = os.path.join(parent_dir, 'Initial_Files', 'FORMIS_2024_July_Bibtex.json')
    logging.info(f"Attempting to export {len(bibtex_records)} records to JSON file: {json_file}")
    export_to_json(bibtex_records, json_file)
    
    # Verify JSON file was created and log its size
    if os.path.exists(json_file):
        file_size = os.path.getsize(json_file)
        logging.info(f"JSON file successfully created at {json_file}")
        logging.info(f"JSON file size: {file_size} bytes")
        
        # Optionally, verify the content of the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        logging.info(f"Verified JSON file. It contains {len(json_data)} records.")
    else:
        logging.error(f"Failed to create JSON file at {json_file}")

    return bibtex_records

if __name__ == "__main__":
    venv_python = create_and_use_venv()
    main(venv_python)