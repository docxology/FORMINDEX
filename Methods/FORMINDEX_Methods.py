import sys
import site
import os
import subprocess
import pkg_resources
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def add_paths():
    """Add necessary paths to sys.path."""
    # Add user site-packages to sys.path
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.insert(0, user_site)

    # Add global site-packages to sys.path
    global_site = site.getsitepackages()
    for path in global_site:
        if path not in sys.path:
            sys.path.append(path)

    # Add the parent directory of the script to the Python path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    sys.path.append(parent_dir)

def install(package):
    """Install a package via pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_virtualenv():
    """Ensure that the script is running inside a virtual environment with required packages."""
    venv_dir = os.path.join(os.path.dirname(__file__), 'venv')

    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])

        # Upgrade pip using the virtual environment's pip
        pip_executable = os.path.join(venv_dir, 'bin', 'pip')  # Linux pip path
        subprocess.check_call([pip_executable, 'install', '--upgrade', 'pip'])

    # Check for required packages and install if missing
    required = {'bibtexparser', 'matplotlib', 'wordcloud', 'scikit-learn', 'numpy'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print(f"Installing missing packages: {missing}")
        pip_executable = os.path.join(venv_dir, 'bin', 'pip')  # Ensure using venv's pip
        for package in missing:
            subprocess.check_call([pip_executable, 'install', package])

def load_bibtex(file_path):
    """Load and parse the BibTeX file."""
    # Ensure the file path is correct
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"The file {absolute_path} does not exist.")
    
    records = process_bibtex(absolute_path)  # Process the BibTeX file
    return records

def process_bibtex(file_path):
    """Process the BibTeX file and extract records with custom parsing."""
    records = []
    current_entry = {}
    entry_type = None
    in_entry = False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            
            if line.startswith('@'):
                # Start of a new entry
                if current_entry:
                    records.append(current_entry)
                current_entry = {}
                entry_type = line[1:].split('{')[0].lower()
                current_entry['ref_type'] = entry_type
                in_entry = True
            elif '=' in line and in_entry:
                # Field in the current entry
                key, value = line.split('=', 1)
                key = key.strip().lower()
                value = value.strip().strip(',').strip()
                if value.startswith('{') and value.endswith('}'):
                    value = value[1:-1]
                current_entry[key] = value
            elif line == '}' and in_entry:
                # End of the current entry
                records.append(current_entry)
                current_entry = {}
                in_entry = False
    
    # Add the last entry if it exists
    if current_entry:
        records.append(current_entry)
    
    return records

def process_endnote_xml(root):
    """Process the parsed EndNote XML and extract records."""
    records = []
    for record in root.findall('.//record'):
        ref_type = record.findtext('.//ref-type').strip() if record.findtext('.//ref-type') else ''
        title = record.findtext('.//titles/title').strip() if record.findtext('.//titles/title') else ''
        author = record.findtext('.//contributors/authors/author').strip() if record.findtext('.//contributors/authors/author') else ''
        secondary_title = (record.findtext('.//secondary-title') or '').strip()  # Handle missing secondary-title

        # Add extraction of missing fields
        journal = record.findtext('.//journal').strip() if record.findtext('.//journal') else ''
        booktitle = record.findtext('.//booktitle').strip() if record.findtext('.//booktitle') else ''
        editor = record.findtext('.//editor').strip() if record.findtext('.//editor') else ''
        publisher = record.findtext('.//publisher').strip() if record.findtext('.//publisher') else ''
        address = record.findtext('.//address').strip() if record.findtext('.//address') else ''
        institution = record.findtext('.//institution').strip() if record.findtext('.//institution') else ''
        volume = record.findtext('.//volume').strip() if record.findtext('.//volume') else ''
        number = record.findtext('.//number').strip() if record.findtext('.//number') else ''
        pages = record.findtext('.//pages').strip() if record.findtext('.//pages') else ''
        year = record.findtext('.//year').strip() if record.findtext('.//year') else ''
        month = record.findtext('.//month').strip() if record.findtext('.//month') else ''
        note = record.findtext('.//note').strip() if record.findtext('.//note') else ''
        abstract = record.findtext('.//abstract').strip() if record.findtext('.//abstract') else ''
        keywords = record.findtext('.//keywords').strip() if record.findtext('.//keywords') else ''
        school = record.findtext('.//school').strip() if record.findtext('.//school') else ''
        type_field = record.findtext('.//type').strip() if record.findtext('.//type') else ''  # Renamed to avoid conflict with Python's 'type'

        records.append({
            'ref_type': ref_type,
            'author': author,
            'title': title,
            'journal': journal,
            'booktitle': booktitle,
            'editor': editor,
            'publisher': publisher,
            'address': address,
            'institution': institution,
            'volume': volume,
            'number': number,
            'pages': pages,
            'year': year,
            'month': month,
            'note': note,
            'abstract': abstract,
            'keywords': keywords,
            'school': school,
            'type': type_field  # Updated key to match extracted value
        })
    return records

def create_histogram(data, title, xlabel, ylabel, filename):
    """Create and save a histogram with improved styling."""
    plt.figure(figsize=(14, 8))
    sns.set_style("whitegrid")
    sns.histplot(data, bins=20, kde=True)
    
    plt.title(title, fontsize=20, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=16, fontweight='bold')
    plt.ylabel(ylabel, fontsize=16, fontweight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_time_series(years, title, ylabel, filename):
    """Create and save a time series plot with improved styling."""
    year_counts = Counter(years)
    sorted_years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in sorted_years]
    
    plt.figure(figsize=(14, 8))
    sns.set_style("whitegrid")
    sns.lineplot(x=sorted_years, y=counts, marker='o', linewidth=2, markersize=8)
    
    plt.title(title, fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=16, fontweight='bold')
    plt.ylabel(ylabel, fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Time series plot created with {len(years)} data points.")
    print(f"Year range: {min(years)} to {max(years)}")

def create_word_cloud(text, title, filename):
    """Create and save a word cloud with improved styling."""
    wordcloud = WordCloud(width=1600, height=800, background_color='white', max_words=200, contour_width=3, contour_color='steelblue').generate(text)
    
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=24, fontweight='bold', pad=20)
    
    plt.tight_layout(pad=0)
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def perform_topic_modeling(texts, n_topics=5, n_top_words=10):
    """Perform topic modeling using LDA."""
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(texts)
    
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(doc_term_matrix)
    
    feature_names = vectorizer.get_feature_names_out()
    
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")
    
    return topics

def plot_top_entities(entities, title, filename, top_n=20):
    """Plot top N entities with improved styling."""
    top_entities = Counter(entities).most_common(top_n)
    entities, counts = zip(*top_entities)
    
    plt.figure(figsize=(14, 10))
    sns.set_style("whitegrid")
    bars = plt.barh(entities, counts)
    
    plt.title(title, fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('Count', fontsize=16, fontweight='bold')
    plt.ylabel('Entity', fontsize=16, fontweight='bold')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    # Add value labels to the end of each bar
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f'{width}', 
                 ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()