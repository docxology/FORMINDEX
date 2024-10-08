import sys
import os
import re

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from Methods.FORMINDEX_Methods import (
    add_paths, ensure_virtualenv, load_bibtex,
    create_histogram, create_time_series, create_word_cloud,
    perform_topic_modeling, plot_top_entities
)
from Scripts.Read_in_FORMIS import main as read_in_formis

def extract_year(year_string):
    # Extract the first 4 consecutive digits from the year string
    match = re.search(r'\d{4}', year_string)
    if match:
        return int(match.group())
    return None

def main():
    # Run Read_in_FORMIS.py
    bibtex_records = read_in_formis()

    # Create output directory
    output_dir = os.path.join(parent_dir, 'Visualizations')
    os.makedirs(output_dir, exist_ok=True)

    # Extract years and create time series
    years = []
    for record in bibtex_records:
        year = record.get('year', '')
        if year:
            extracted_year = extract_year(year)
            if extracted_year:
                years.append(extracted_year)

    if years:
        create_time_series(years, 'Publications per Year', 'Number of Publications', os.path.join(output_dir, 'publications_per_year.png'))
    else:
        print("No valid years found in the dataset.")

    print(f"Total records: {len(bibtex_records)}")
    print(f"Records with valid years: {len(years)}")
    print(f"Sample of years: {years[:10]}")  # Print first 10 years

    # Create word cloud from titles
    titles = ' '.join([record.get('title', '') for record in bibtex_records])
    create_word_cloud(titles, 'Title Word Cloud', os.path.join(output_dir, 'title_word_cloud.png'))

    # Create word cloud from abstracts
    abstracts = ' '.join([record.get('abstract', '') for record in bibtex_records])
    create_word_cloud(abstracts, 'Abstract Word Cloud', os.path.join(output_dir, 'abstract_word_cloud.png'))

    # Perform topic modeling on abstracts
    abstract_texts = [record.get('abstract', '') for record in bibtex_records if record.get('abstract')]
    topics = perform_topic_modeling(abstract_texts)
    with open(os.path.join(output_dir, 'topics.txt'), 'w') as f:
        f.write('\n'.join(topics))

    # Plot top authors
    authors = [author.strip() for record in bibtex_records for author in record.get('author', '').split(' and ')]
    plot_top_entities(authors, 'Top 20 Authors', os.path.join(output_dir, 'top_authors.png'))

    # Plot top journals/conferences
    venues = [record.get('journal', '') or record.get('booktitle', '') for record in bibtex_records]
    plot_top_entities(venues, 'Top 20 Venues', os.path.join(output_dir, 'top_venues.png'))

    # Create histogram of reference types
    ref_types = [record.get('ref_type', '') for record in bibtex_records]
    create_histogram(ref_types, 'Distribution of Reference Types', 'Reference Type', 'Count', os.path.join(output_dir, 'ref_type_distribution.png'))

    print("Visualizations have been created and saved in the 'Visualizations' directory.")

if __name__ == "__main__":
    main()
