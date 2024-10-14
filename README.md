[![DOI](https://zenodo.org/badge/869508969.svg)](https://doi.org/10.5281/zenodo.13927024)

# FORMINDEX: FORMIS INtegrated Database EXploration

## Overview

FORMINDEX is a comprehensive project aimed at analyzing and visualizing the FORMIS myrmecological database. It combines advanced bibliometric techniques, artificial intelligence, and interactive visualizations to extract insights from published ant research.

## Key Components

1. Metadata-Centric Analysis
2. Fair Use Compliance
3. LLM Integration
4. Dynamic Visualization
5. Longitudinal Analysis
6. AI-Driven Synthesis
7. Targeted Bibliography Generation
8. Multi-modal Output (Podcasts, Summaries, Translations)

## Methodology

### 1. Data Ingestion and Processing

- Full coverage of FORMIS database (July 2024 export, ~80,000 records)
- Conversion of Bibtex to JSON format
- Generation of targeted bibliographies based on key terms

### 2. Analysis Techniques

#### Quantitative Methods:
- Frequency analysis of record types, authors, venues, and locations
- Network analysis of co-authorship
- Temporal analysis of publications and venues

#### Qualitative Methods:
- Thematic analysis through word clouds
- Content analysis via AI-generated summaries
- Narrative synthesis through AI-generated podcasts

### 3. AI and Machine Learning Integration

- Use of NotebookLM for generating conversational podcasts
- OpenAI API integration for summarization and translation
- Perplexity AI for internet-enabled myrmecological inquiries

### 4. Visualization and Presentation

- Interactive charts for publication trends, author networks, and topic distributions
- Word clouds for title and abstract analysis
- Automated generation of summary reports and translations

## Project Structure

- `Read_in_FORMIS.py`: Ingests Bibtex and stores records in JSON format
- `Generate_Target_Bibliographies.py`: Creates subsets of records based on key terms
- `Visualize_FORMIS.py`: Generates visualizations for full FORMIS and targeted bibliographies
- `LLM_Methods/`: Scripts for AI-driven summarization and translation
- `Perplexity_Methods/`: Scripts for advanced myrmecological inquiries using Perplexity AI

## Outputs

1. Comprehensive bibliographic analysis visualizations
2. AI-generated literature summaries in multiple languages
3. Conversational podcasts on targeted myrmecological topics
4. Internet-enabled myrmecological inquiry results

## Ethical Considerations

- Strict adherence to fair use and copyright regulations
- Responsible use of AI technologies

## Future Directions

- Integration with multi-omic phenotypic data
- Development of predictive models for research trends
- Expansion of analysis techniques to other entomological databases
- Integration with NCBI species ID for broader MetaInformAnt efforts
- Collaboration with FORMIS stakeholders for continuous improvement

## How to Use

1. Clone the repository
2. Install required dependencies (list to be provided)
3. Run `Read_in_FORMIS.py` to ingest the FORMIS database
4. Use `Generate_Target_Bibliographies.py` to create subsets of interest
5. Execute `Visualize_FORMIS.py` for comprehensive visualizations
6. Explore `LLM_Methods/` and `Perplexity_Methods/` for AI-driven analyses

## Contributing

We welcome contributions! Please see our contributing guidelines (link to be added) for more information.

## License

This project is licensed under [LICENSE NAME] - see the LICENSE.md file for details.

## Acknowledgments

- FORMIS database maintainers
- Contributors to open-source libraries used in this project

For more information, visit our [project website](https://github.com/docxology/FORMINDEX) or contact [Your Contact Information].
