import json
from collections import Counter
from typing import List, Dict
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

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

def analyze_locations(formis_data: List[Dict]) -> Counter:
    """
    Analyze locations mentioned in the FORMIS database.
    
    Args:
        formis_data (List[Dict]): List of paper entries from the FORMIS database.
    
    Returns:
        Counter: Counter of locations mentioned in the papers.
    """
    locations = []
    for paper in formis_data:
        if 'address' in paper and paper['address']:
            # Split the address by comma and take the last part as the country
            country = paper['address'].split(',')[-1].strip()
            locations.append(country)
    return Counter(locations)

def create_location_bar_chart(location_counter: Counter, output_path: str, title: str):
    """
    Create a bar chart of the top 20 locations.
    
    Args:
        location_counter (Counter): Counter of locations.
        output_path (str): Path to save the output image.
        title (str): Title of the chart.
    """
    top_20 = location_counter.most_common(20)
    locations, counts = zip(*top_20)

    plt.figure(figsize=(12, 8))
    sns.barplot(x=list(counts), y=list(locations))
    plt.title(title)
    plt.xlabel('Number of Papers')
    plt.ylabel('Location')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_location_wordcloud(location_counter: Counter, output_path: str):
    """
    Create a word cloud of locations.
    
    Args:
        location_counter (Counter): Counter of locations.
        output_path (str): Path to save the output image.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(location_counter)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(output_path)
    plt.close()

def analyze_and_visualize(file_path: str, output_dir: str, prefix: str = ''):
    """
    Analyze keywords and locations, and create visualizations.
    
    Args:
        file_path (str): Path to the FORMIS JSON file.
        output_dir (str): Directory to save output files.
        prefix (str): Prefix for output files (default: '').
    """
    formis_data = load_formis_data(file_path)
    
    # Keyword analysis
    keyword_counter, species_case_counter, total_papers, papers_with_keywords, min_keywords, max_keywords, avg_keywords = analyze_keywords(file_path)
    
    # Location analysis
    location_counter = analyze_locations(formis_data)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create visualizations
    create_location_bar_chart(location_counter, os.path.join(output_dir, f'{prefix}top_20_locations.png'), f'Top 20 Locations in {prefix}Literature')
    create_location_wordcloud(location_counter, os.path.join(output_dir, f'{prefix}location_wordcloud.png'))
    
    # Write analysis results to a file
    with open(os.path.join(output_dir, f'{prefix}keyword_location_analysis.txt'), 'w') as f:
        f.write(f"Analysis Results for {prefix}Literature\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total number of papers: {total_papers}\n")
        f.write(f"Number of papers with keywords: {papers_with_keywords}\n")
        f.write(f"Percentage of papers with keywords: {papers_with_keywords/total_papers*100:.2f}%\n")
        f.write(f"Range of keywords per paper: {min_keywords} to {max_keywords}\n")
        f.write(f"Average number of keywords per paper: {avg_keywords:.2f}\n\n")
        
        f.write("Top 20 most common keywords:\n")
        for keyword, count in keyword_counter.most_common(20):
            f.write(f"{keyword}: {count}\n")
        
        f.write("\nTop 20 most common 'Species case' keywords:\n")
        for keyword, count in species_case_counter.most_common(20):
            f.write(f"{keyword}: {count}\n")
        
        f.write("\nTop 20 most common locations:\n")
        for location, count in location_counter.most_common(20):
            f.write(f"{location}: {count}\n")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    formis_file = os.path.join(script_dir, "..", "Initial_Files", "FORMIS_2024_July_Bibtex.json")
    
    if not os.path.exists(formis_file):
        print(f"Error: File not found: {formis_file}")
        print("Please make sure the FORMIS JSON file is in the correct location.")
        exit(1)
    
    # Analyze and visualize for all literature
    output_dir = os.path.join(script_dir, "..", "Visualizations", "All_Literature")
    analyze_and_visualize(formis_file, output_dir)
    
    # Analyze and visualize for targeted bibliographies
    targeted_bib_dir = os.path.join(script_dir, "..", "Targeted_Bibliographies")
    for folder in os.listdir(targeted_bib_dir):
        folder_path = os.path.join(targeted_bib_dir, folder)
        if os.path.isdir(folder_path):
            json_files = [f for f in os.listdir(folder_path) if f.endswith('_bibliography.json')]
            for json_file in json_files:
                file_path = os.path.join(folder_path, json_file)
                prefix = json_file.replace('_bibliography.json', '_')
                output_dir = os.path.join(script_dir, "..", "Visualizations", f"{prefix[:-1]}_Literature")
                analyze_and_visualize(file_path, output_dir, prefix)
    
    print("Keyword and location analysis completed. Results and visualizations have been saved.")