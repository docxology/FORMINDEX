#!/usr/bin/env python3
"""
This script should be run from the project's root directory after activating the virtual environment.
"""
import sys
import os
import re
import json
from collections import defaultdict
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from Location_Analysis import create_world_map_publications

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from Methods.FORMINDEX_Methods import (
    add_paths, ensure_virtualenv, create_histogram, create_time_series,
    create_word_cloud, perform_topic_modeling, plot_top_entities
)

def extract_year(year_string):
    match = re.search(r'\d{4}', year_string)
    return int(match.group()) if match else None

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_stacked_area_chart(bibtex_records, output_dir):
    year_venue = defaultdict(lambda: defaultdict(int))
    for record in bibtex_records:
        year = extract_year(record.get('year', ''))
        venue = record.get('journal', '') or record.get('booktitle', '')
        if year and venue:
            year_venue[year][venue] += 1
    
    years = sorted(year_venue.keys())
    venues = sorted(set(venue for venues in year_venue.values() for venue in venues))
    top_venues = sorted(venues, key=lambda v: sum(year_venue[y][v] for y in years), reverse=True)[:10]
    
    data = np.array([[year_venue[year][venue] for venue in top_venues] for year in years])
    
    plt.figure(figsize=(16, 10))
    plt.stackplot(years, data.T, labels=top_venues)
    plt.title('Evolution of Top Venues Over Time', fontsize=20, fontweight='bold')
    plt.xlabel('Year', fontsize=16)
    plt.ylabel('Number of Publications', fontsize=16)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'venue_evolution.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_coauthorship_heatmap(bibtex_records, output_dir):
    """Create a larger, half-matrix heatmap of coauthorship."""
    author_pairs = []
    for record in bibtex_records:
        authors = record.get('author', '').split(' and ')
        authors = [author.strip() for author in authors if author.strip()]
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                author_pairs.append(tuple(sorted([authors[i], authors[j]])))

    # Count co-authorships
    coauthorship_counts = Counter(author_pairs)

    # Get top authors
    top_authors = [author for pair in coauthorship_counts.most_common(30) for author in pair[0]]
    top_authors = list(dict.fromkeys(top_authors))  # Remove duplicates while preserving order

    # Create coauthorship matrix (upper triangular)
    n = len(top_authors)
    coauthorship_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            count = coauthorship_counts.get(tuple(sorted([top_authors[i], top_authors[j]])), 0)
            coauthorship_matrix[i, j] = count

    # Create mask for lower triangular part
    mask = np.tril(np.ones_like(coauthorship_matrix, dtype=bool))

    # Create heatmap
    plt.figure(figsize=(20, 16))
    sns.set(font_scale=1.2)
    
    ax = sns.heatmap(coauthorship_matrix, 
                     mask=mask,
                     annot=True, 
                     fmt='.0f', 
                     cmap='YlGnBu', 
                     xticklabels=top_authors, 
                     yticklabels=top_authors,
                     square=True,
                     cbar_kws={'label': 'Number of Co-authored Papers'})
    
    plt.title('Coauthorship Heatmap', fontsize=24, pad=20)
    plt.xlabel('Authors', fontsize=18, labelpad=10)
    plt.ylabel('Authors', fontsize=18, labelpad=10)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'coauthorship_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Coauthorship heatmap created with {len(top_authors)} top authors.")

def create_ref_type_pie_chart(bibtex_records, output_dir):
    ref_types = [record.get('ref_type', '') for record in bibtex_records]
    ref_type_counts = defaultdict(int)
    for rt in ref_types:
        if rt:
            ref_type_counts[rt] += 1
    
    plt.figure(figsize=(12, 8))
    plt.pie(ref_type_counts.values(), labels=ref_type_counts.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Distribution of Reference Types', fontsize=20, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ref_type_distribution_pie.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_location_distribution(bibtex_records, output_dir):
    locations = [record.get('address', '').split(',')[-1].strip() for record in bibtex_records]
    location_counts = defaultdict(int)
    for location in locations:
        if location:
            location_counts[location] += 1
    
    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    plt.figure(figsize=(14, 10))
    sns.barplot(x=[count for _, count in top_locations], y=[location for location, _ in top_locations])
    plt.title('Top 20 Locations by Number of Publications', fontsize=20, fontweight='bold')
    plt.xlabel('Number of Publications', fontsize=16)
    plt.ylabel('Location', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'location_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Location distribution plot created with {len(top_locations)} top locations.")

def create_citations_scatter(bibtex_records, output_dir):
    years = []
    citations = []
    for record in bibtex_records:
        year = extract_year(record.get('year', ''))
        citation = record.get('cited_by', '')
        if year and citation:
            try:
                citation_count = int(citation)
                years.append(year)
                citations.append(citation_count)
            except ValueError:
                print(f"Invalid citation count: {citation} for year {year}")

    if not years or not citations:
        print("No valid citation data found. Unable to create citations scatter plot.")
        return

    plt.figure(figsize=(14, 10))
    plt.scatter(years, citations, alpha=0.5)
    plt.title('Publications per Year vs. Citations', fontsize=20, fontweight='bold')
    plt.xlabel('Year', fontsize=16)
    plt.ylabel('Number of Citations', fontsize=16)
    plt.yscale('log')  # Use log scale for citations
    plt.xscale('log')  # Use log scale for years to spread out older publications
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'citations_scatter.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Citations scatter plot created with {len(years)} data points.")
    print(f"Year range: {min(years)} to {max(years)}")
    print(f"Citation range: {min(citations)} to {max(citations)}")

def main():
    json_file_path = os.path.join(parent_dir, 'Initial_Files', 'FORMIS_2024_July_Bibtex.json')
    bibtex_records = load_json_data(json_file_path)

    output_dir = os.path.join(parent_dir, 'Visualizations')
    os.makedirs(output_dir, exist_ok=True)

    years = [extract_year(record.get('year', '')) for record in bibtex_records if extract_year(record.get('year', ''))]

    if years:
        create_time_series(years, 'Publications per Year', 'Number of Publications', os.path.join(output_dir, 'publications_per_year.png'))
    else:
        print("No valid years found in the dataset.")

    print(f"Total records: {len(bibtex_records)}")
    print(f"Records with valid years: {len(years)}")
    print(f"Sample of years: {years[:10]}")

    titles = ' '.join([record.get('title', '') for record in bibtex_records])
    create_word_cloud(titles, 'Title Word Cloud', os.path.join(output_dir, 'title_word_cloud.png'))

    abstracts = ' '.join([record.get('abstract', '') for record in bibtex_records])
    create_word_cloud(abstracts, 'Abstract Word Cloud', os.path.join(output_dir, 'abstract_word_cloud.png'))

    abstract_texts = [record.get('abstract', '') for record in bibtex_records if record.get('abstract')]
    topics, doc_topic_dist = perform_topic_modeling(abstract_texts)
    
    with open(os.path.join(output_dir, 'topics.txt'), 'w') as f:
        f.write("Topic Modeling Results\n")
        f.write("======================\n\n")
        for topic in topics:
            f.write(f"Topic {topic['id']} (Strength: {topic['strength']:.2f}):\n")
            f.write(", ".join(topic['words']) + "\n\n")
        
        f.write("\nTop Documents for Each Topic:\n")
        f.write("=============================\n\n")
        for i, topic in enumerate(topics):
            f.write(f"Topic {topic['id']}:\n")
            top_doc_indices = doc_topic_dist[:, i].argsort()[-5:][::-1]
            for idx in top_doc_indices:
                doc_strength = doc_topic_dist[idx, i]
                doc_title = bibtex_records[idx].get('title', 'No title')
                f.write(f"  - {doc_title} (Strength: {doc_strength:.2f})\n")
            f.write("\n")

    print(f"Enhanced topic modeling results saved to {os.path.join(output_dir, 'topics.txt')}")

    authors = [author.strip() for record in bibtex_records for author in record.get('author', '').split(' and ')]
    plot_top_entities(authors, 'Top 20 Authors', os.path.join(output_dir, 'top_authors.png'))

    venues = [record.get('journal', '') or record.get('booktitle', '') for record in bibtex_records]
    venues = [venue.strip() for venue in venues if venue and venue.strip()]
    plot_top_entities(venues, 'Top 20 Venues', os.path.join(output_dir, 'top_venues.png'))

    ref_types = [record.get('ref_type', '') for record in bibtex_records]
    ref_types = [rt for rt in ref_types if rt]
    create_histogram(ref_types, 'Distribution of Reference Types', 'Count', 'Reference Type', os.path.join(output_dir, 'ref_type_distribution.png'))

    # New visualizations
    create_stacked_area_chart(bibtex_records, output_dir)
    create_coauthorship_heatmap(bibtex_records, output_dir)
    create_ref_type_pie_chart(bibtex_records, output_dir)
    create_location_distribution(bibtex_records, output_dir)  # Updated function name
    create_citations_scatter(bibtex_records, output_dir)
    create_world_map_publications(bibtex_records, output_dir)

    print("Visualizations have been created and saved in the 'Visualizations' directory.")

if __name__ == "__main__":
    main()