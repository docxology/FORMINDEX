import json
from collections import Counter
from typing import List, Dict
import os
import re

def load_formis_data(file_path: str) -> List[Dict]:
    """
    Load FORMIS data from a JSON file.
    
    Args:
        file_path (str): Path to the FORMIS JSON file.
    
    Returns:
        List[Dict]: List of paper entries from the FORMIS database.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_paper_keywords(paper: Dict) -> List[str]:
    """
    Process a single paper entry and extract keywords.
    
    Args:
        paper (Dict): A single paper entry from the FORMIS database.
    
    Returns:
        List[str]: List of keywords found in the paper.
    """
    if 'keywords' in paper and paper['keywords']:
        # Split the keywords string by semicolon and strip whitespace
        return [keyword.strip() for keyword in paper['keywords'].split(';') if keyword.strip()]
    return []

def is_species_case(keyword: str) -> bool:
    """
    Check if a keyword follows the "Species case" pattern.
    
    Args:
        keyword (str): The keyword to check.
    
    Returns:
        bool: True if the keyword follows the pattern, False otherwise.
    """
    pattern = r'^[A-Z][a-z]+\s+[a-z]+$'
    return bool(re.match(pattern, keyword))

def analyze_keywords(file_path: str) -> tuple:
    """
    Analyze keywords in the FORMIS database.
    
    Args:
        file_path (str): Path to the FORMIS JSON file.
    
    Returns:
        tuple: (Counter of keywords, Counter of species case keywords, total papers, papers with keywords, min keywords, max keywords, avg keywords)
    """
    formis_data = load_formis_data(file_path)
    all_keywords = []
    species_case_keywords = []
    papers_with_keywords = 0
    total_papers = len(formis_data)
    keyword_counts = []
    
    for paper in formis_data:
        keywords = process_paper_keywords(paper)
        if keywords:
            papers_with_keywords += 1
            all_keywords.extend(keywords)
            species_case_keywords.extend([kw for kw in keywords if is_species_case(kw)])
            keyword_counts.append(len(keywords))
    
    min_keywords = min(keyword_counts) if keyword_counts else 0
    max_keywords = max(keyword_counts) if keyword_counts else 0
    avg_keywords = sum(keyword_counts) / len(keyword_counts) if keyword_counts else 0
    
    return Counter(all_keywords), Counter(species_case_keywords), total_papers, papers_with_keywords, min_keywords, max_keywords, avg_keywords

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    formis_file = os.path.join(script_dir, "..", "Initial_Files", "FORMIS_2024_July_Bibtex.json")
    
    if not os.path.exists(formis_file):
        print(f"Error: File not found: {formis_file}")
        print("Please make sure the FORMIS JSON file is in the correct location.")
        exit(1)
    
    keyword_counter, species_case_counter, total_papers, papers_with_keywords, min_keywords, max_keywords, avg_keywords = analyze_keywords(formis_file)
    
    print(f"Total number of papers: {total_papers}")
    print(f"Number of papers with keywords: {papers_with_keywords}")
    print(f"Percentage of papers with keywords: {papers_with_keywords/total_papers*100:.2f}%")
    print(f"Range of keywords per paper: {min_keywords} to {max_keywords}")
    print(f"Average number of keywords per paper: {avg_keywords:.2f}")
    
    print("\nTop 20 most common keywords:")
    for keyword, count in keyword_counter.most_common(20):
        print(f"{keyword}: {count}")
    
    print("\nTop 20 most common 'Species case' keywords:")
    for keyword, count in species_case_counter.most_common(20):
        print(f"{keyword}: {count}")