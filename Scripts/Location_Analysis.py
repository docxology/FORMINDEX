#!/usr/bin/env python3
"""
This script analyzes location data from FORMIS publications and creates a world map heatmap.
It should be run from the Scripts/ folder.
"""
import os
import json
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_country_coordinates():
    # This is a simplified dictionary of country coordinates
    # You may want to expand this with more accurate data
    return {
        "USA": (38, -97),
        "UK": (54, -2),
        "Germany": (51, 9),
        "France": (46, 2),
        "Japan": (36, 138),
        "China": (35, 105),
        "Australia": (-25, 133),
        "Canada": (56, -106),
        "Italy": (42, 12),
        "Spain": (40, -4),
        # Add more countries as needed
    }

def create_world_map_heatmap(bibtex_records, output_dir):
    # Extract locations from the records
    locations = [record.get('address', '').split(',')[-1].strip() for record in bibtex_records]
    location_counts = Counter(location for location in locations if location)

    # Get country coordinates
    country_coords = get_country_coordinates()

    # Create world map
    plt.figure(figsize=(20, 10))
    
    # Create a simple world map background
    plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)  # Equator
    plt.axvline(x=0, color='k', linestyle='-', linewidth=0.5)  # Prime Meridian
    
    # Add continent outlines (very simplified)
    continents = {
        'North America': [(-170, 15), (-50, 70)],
        'South America': [(-80, -60), (-35, 15)],
        'Europe': [(-10, 35), (40, 70)],
        'Africa': [(-20, -35), (50, 35)],
        'Asia': [(60, 0), (150, 70)],
        'Australia': [(110, -45), (155, -10)]
    }
    
    for continent, (bottom_left, top_right) in continents.items():
        plt.plot([bottom_left[0], bottom_left[0], top_right[0], top_right[0], bottom_left[0]],
                 [bottom_left[1], top_right[1], top_right[1], bottom_left[1], bottom_left[1]],
                 'k-', linewidth=0.5)

    # Create a custom colormap
    colors = ['#FFA07A', '#FF7F50', '#FF6347', '#FF4500', '#FF0000']
    n_bins = len(colors)
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

    # Plot locations
    for country, count in location_counts.items():
        if country in country_coords:
            lat, lon = country_coords[country]
            plt.scatter(lon, lat, s=count*10, c=[count], cmap=cmap, alpha=0.7, vmin=0, vmax=max(location_counts.values()))
            plt.annotate(country, (lon, lat), xytext=(3, 3), textcoords="offset points", fontsize=8, alpha=0.8)

    plt.colorbar(label='Number of Publications', orientation='vertical', shrink=0.7)
    plt.title('World Map of Publications', fontsize=20, fontweight='bold')
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()

    # Save the chart
    plt.savefig(os.path.join(output_dir, 'world_map_publications_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print("World map of publications heatmap created and saved.")

def main():
    # Adjust the path to work from the Scripts/ folder
    json_file_path = os.path.join('..', 'Initial_Files', 'FORMIS_2024_July_Bibtex.json')
    bibtex_records = load_json_data(json_file_path)

    output_dir = os.path.join('..', 'Visualizations')
    os.makedirs(output_dir, exist_ok=True)

    create_world_map_heatmap(bibtex_records, output_dir)

if __name__ == "__main__":
    main()
