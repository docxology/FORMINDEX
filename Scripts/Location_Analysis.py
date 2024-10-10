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
import random

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_country_coordinates():
    # A more comprehensive list of country coordinates
    return {
        "Afghanistan": (33.93911, 67.709953), "Albania": (41.153332, 20.168331),
        "Algeria": (28.033886, 1.659626), "Andorra": (42.546245, 1.601554),
        "Angola": (-11.202692, 17.873887), "Argentina": (-38.416097, -63.616672),
        "Armenia": (40.069099, 45.038189), "Australia": (-25.274398, 133.775136),
        "Austria": (47.516231, 14.550072), "Azerbaijan": (40.143105, 47.576927),
        "Bahrain": (25.930414, 50.637772), "Bangladesh": (23.684994, 90.356331),
        "Belarus": (53.709807, 27.953389), "Belgium": (50.503887, 4.469936),
        "Bhutan": (27.514162, 90.433601), "Bolivia": (-16.290154, -63.588653),
        "Bosnia and Herzegovina": (43.915886, 17.679076), "Botswana": (-22.328474, 24.684866),
        "Brazil": (-14.235004, -51.92528), "Brunei": (4.535277, 114.727669),
        "Bulgaria": (42.733883, 25.48583), "Burkina Faso": (12.238333, -1.561593),
        "Burundi": (-3.373056, 29.918886), "Cambodia": (12.565679, 104.990963),
        "Cameroon": (7.369722, 12.354722), "Canada": (56.130366, -106.346771),
        "Central African Republic": (6.611111, 20.939444), "Chad": (15.454166, 18.732207),
        "Chile": (-35.675147, -71.542969), "China": (35.86166, 104.195397),
        "Colombia": (4.570868, -74.297333), "Congo": (-0.228021, 15.827659),
        "Costa Rica": (9.748917, -83.753428), "Croatia": (45.1, 15.2),
        "Cuba": (21.521757, -77.781167), "Cyprus": (35.126413, 33.429859),
        "Czech Republic": (49.817492, 15.472962), "Denmark": (56.26392, 9.501785),
        "Djibouti": (11.825138, 42.590275), "Dominican Republic": (18.735693, -70.162651),
        "Ecuador": (-1.831239, -78.183406), "Egypt": (26.820553, 30.802498),
        "El Salvador": (13.794185, -88.89653), "Equatorial Guinea": (1.650801, 10.267895),
        "Eritrea": (15.179384, 39.782334), "Estonia": (58.595272, 25.013607),
        "Ethiopia": (9.145, 40.489673), "Fiji": (-16.578193, 179.414413),
        "Finland": (61.92411, 25.748151), "France": (46.227638, 2.213749),
        "Gabon": (-0.803689, 11.609444), "Georgia": (42.315407, 43.356892),
        "Germany": (51.165691, 10.451526), "Ghana": (7.946527, -1.023194),
        "Greece": (39.074208, 21.824312), "Guatemala": (15.783471, -90.230759),
        "Guinea": (9.945587, -9.696645), "Haiti": (18.971187, -72.285215),
        "Honduras": (15.199999, -86.241905), "Hungary": (47.162494, 19.503304),
        "Iceland": (64.963051, -19.020835), "India": (20.593684, 78.96288),
        "Indonesia": (-0.789275, 113.921327), "Iran": (32.427908, 53.688046),
        "Iraq": (33.223191, 43.679291), "Ireland": (53.41291, -8.24389),
        "Israel": (31.046051, 34.851612), "Italy": (41.87194, 12.56738),
        "Jamaica": (18.109581, -77.297508), "Japan": (36.204824, 138.252924),
        "Jordan": (30.585164, 36.238414), "Kazakhstan": (48.019573, 66.923684),
        "Kenya": (-0.023559, 37.906193), "Kuwait": (29.31166, 47.481766),
        "Kyrgyzstan": (41.20438, 74.766098), "Laos": (19.85627, 102.495496),
        "Latvia": (56.879635, 24.603189), "Lebanon": (33.854721, 35.862285),
        "Lesotho": (-29.609988, 28.233608), "Liberia": (6.428055, -9.429499),
        "Libya": (26.3351, 17.228331), "Liechtenstein": (47.166, 9.555373),
        "Lithuania": (55.169438, 23.881275), "Luxembourg": (49.815273, 6.129583),
        "Madagascar": (-18.766947, 46.869107), "Malawi": (-13.254308, 34.301525),
        "Malaysia": (4.210484, 101.975766), "Maldives": (3.202778, 73.22068),
        "Mali": (17.570692, -3.996166), "Malta": (35.937496, 14.375416),
        "Mauritania": (21.00789, -10.940835), "Mauritius": (-20.348404, 57.552152),
        "Mexico": (23.634501, -102.552784), "Moldova": (47.411631, 28.369885),
        "Monaco": (43.750298, 7.412841), "Mongolia": (46.862496, 103.846656),
        "Montenegro": (42.708678, 19.37439), "Morocco": (31.791702, -7.09262),
        "Mozambique": (-18.665695, 35.529562), "Myanmar": (21.913965, 95.956223),
        "Namibia": (-22.95764, 18.49041), "Nepal": (28.394857, 84.124008),
        "Netherlands": (52.132633, 5.291266), "New Zealand": (-40.900557, 174.885971),
        "Nicaragua": (12.865416, -85.207229), "Niger": (17.607789, 8.081666),
        "Nigeria": (9.081999, 8.675277), "North Korea": (40.339852, 127.510093),
        "North Macedonia": (41.608635, 21.745275), "Norway": (60.472024, 8.468946),
        "Oman": (21.512583, 55.923255), "Pakistan": (30.375321, 69.345116),
        "Palestine": (31.952162, 35.233154), "Panama": (8.537981, -80.782127),
        "Papua New Guinea": (-6.314993, 143.95555), "Paraguay": (-23.442503, -58.443832),
        "Peru": (-9.189967, -75.015152), "Philippines": (12.879721, 121.774017),
        "Poland": (51.919438, 19.145136), "Portugal": (39.399872, -8.224454),
        "Qatar": (25.354826, 51.183884), "Romania": (45.943161, 24.96676),
        "Russia": (61.52401, 105.318756), "Rwanda": (-1.940278, 29.873888),
        "Saudi Arabia": (23.885942, 45.079162), "Senegal": (14.497401, -14.452362),
        "Serbia": (44.016521, 21.005859), "Sierra Leone": (8.460555, -11.779889),
        "Singapore": (1.352083, 103.819836), "Slovakia": (48.669026, 19.699024),
        "Slovenia": (46.151241, 14.995463), "Somalia": (5.152149, 46.199616),
        "South Africa": (-30.559482, 22.937506), "South Korea": (35.907757, 127.766922),
        "South Sudan": (6.876991, 31.306978), "Spain": (40.463667, -3.74922),
        "Sri Lanka": (7.873054, 80.771797), "Sudan": (12.862807, 30.217636),
        "Suriname": (3.919305, -56.027783), "Sweden": (60.128161, 18.643501),
        "Switzerland": (46.818188, 8.227512), "Syria": (34.802075, 38.996815),
        "Taiwan": (23.69781, 120.960515), "Tajikistan": (38.861034, 71.276093),
        "Tanzania": (-6.369028, 34.888822), "Thailand": (15.870032, 100.992541),
        "Togo": (8.619543, 0.824782), "Tunisia": (33.886917, 9.537499),
        "Turkey": (38.963745, 35.243322), "Turkmenistan": (38.969719, 59.556278),
        "Uganda": (1.373333, 32.290275), "Ukraine": (48.379433, 31.16558),
        "United Arab Emirates": (23.424076, 53.847818), "United Kingdom": (55.378051, -3.435973),
        "United States": (37.09024, -95.712891), "Uruguay": (-32.522779, -55.765835),
        "Uzbekistan": (41.377491, 64.585262), "Vatican City": (41.902916, 12.453389),
        "Venezuela": (6.42375, -66.58973), "Vietnam": (14.058324, 108.277199),
        "Yemen": (15.552727, 48.516388), "Zambia": (-13.133897, 27.849332),
        "Zimbabwe": (-19.015438, 29.154857)
    }

def estimate_city_location(city, country, country_coords):
    if country in country_coords:
        lat, lon = country_coords[country]
        # Add some random offset to distinguish cities within the same country
        lat_offset = random.uniform(-2, 2)
        lon_offset = random.uniform(-2, 2)
        return lat + lat_offset, lon + lon_offset
    return None

def create_world_map_heatmap(bibtex_records, output_dir):
    # Extract locations from the records
    locations = [record.get('address', '').split(',') for record in bibtex_records]
    locations = [loc for loc in locations if len(loc) >= 2]

    # Separate cities and countries
    cities = [loc[-2].strip() for loc in locations]
    countries = [loc[-1].strip() for loc in locations]

    # Count occurrences
    location_counts = Counter(zip(cities, countries))

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
    for (city, country), count in location_counts.items():
        if country in country_coords:
            lat, lon = country_coords[country]
            plt.scatter(lon, lat, s=count*10, c=[count], cmap=cmap, alpha=0.7, vmin=0, vmax=max(location_counts.values()))
            plt.annotate(f"{country}", (lon, lat), xytext=(3, 3), textcoords="offset points", fontsize=8, alpha=0.8)
        
        # Estimate and plot city location
        city_loc = estimate_city_location(city, country, country_coords)
        if city_loc:
            lat, lon = city_loc
            plt.scatter(lon, lat, s=count*5, c='blue', alpha=0.5)
            plt.annotate(f"{city}", (lon, lat), xytext=(3, 3), textcoords="offset points", fontsize=6, alpha=0.6)

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