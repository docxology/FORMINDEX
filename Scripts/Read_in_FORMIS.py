import sys
import os

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from Methods.FORMINDEX_Methods import add_paths, ensure_virtualenv, load_bibtex

def main():
    add_paths()
    ensure_virtualenv()

    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"sys.path: {sys.path}")
    
    try:
        import bibtexparser
        print("bibtexparser successfully imported")
    except ImportError as e:
        print(f"Error importing bibtexparser: {e}")
        print("Attempting to install bibtexparser...")
        from Methods.FORMINDEX_Methods import install
        install('bibtexparser')
        print("Installation complete. Trying import again...")
        try:
            import bibtexparser
            print("bibtexparser successfully imported after installation")
        except ImportError as e:
            print(f"Error importing bibtexparser after installation: {e}")
    
    # Load BibTeX records
    bibtex_file = os.path.join(parent_dir, 'Initial_Files', 'FORMIS 2024(July)-Bibtext.txt')
    bibtex_records = load_bibtex(bibtex_file)
    print(f"Loaded {len(bibtex_records)} BibTeX records.")  # Log the number of BibTeX records
    
    # Count each @ resource
    resource_counts = {}
    for record in bibtex_records:
        ref_type = record.get('ref_type', 'unknown')
        resource_counts[ref_type] = resource_counts.get(ref_type, 0) + 1

    print("BibTeX resource counts:")
    for ref_type, count in resource_counts.items():
        print(f"{ref_type}: {count}")
    
    # Print the first few records for verification
    print("\nFirst few records:")
    for i, record in enumerate(bibtex_records[:5]):  # Print first 5 records
        print(f"Record {i+1}:")
        for key, value in record.items():
            print(f"  {key}: {value}")
        print()

    return bibtex_records

if __name__ == "__main__":
    main()