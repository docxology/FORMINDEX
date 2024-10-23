import os
import sys
import logging
import argparse
from typing import List, Tuple
import numpy as np
import spacy

from Visualization_Methods import (
    read_markdown_files, preprocess_text, perform_tfidf_and_dim_reduction,
    plot_dimension_reduction, plot_word_importance, plot_pca_eigen_terms,
    create_word_cloud, plot_prompt_distribution, plot_topic_modeling,
    plot_heatmap, plot_confidence_intervals, plot_system_prompt_comparison,
    plot_term_frequency_distribution, plot_term_network,
    extract_prompt_info, plot_pca_scree, plot_pca_cumulative_variance,
    plot_pca_loadings_heatmap, save_pca_top_features, plot_pca_3d
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_introductions_folder(start_path: str) -> str:
    """
    Recursively search for the 'Introductions' folder starting from the given path.
    """
    for root, dirs, _ in os.walk(start_path):
        if 'Introductions' in dirs:
            return os.path.join(root, 'Introductions')
    return None

def main(input_folder: str, output_folder: str) -> None:
    logger.info(f"Starting semantic analysis for folder: {input_folder}")
    
    if not os.path.isdir(input_folder):
        logger.error(f"The specified input path is not a valid directory: {input_folder}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir(os.path.dirname(input_folder))}")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to load spaCy model: {str(e)}")
        sys.exit(1)
    
    # Read documents
    documents, filenames, labels = read_markdown_files(input_folder)
    
    if not documents:
        logger.warning("No markdown files found in the specified directory.")
        return
    
    logger.info(f"Found {len(documents)} markdown files.")
    
    # Preprocess documents
    preprocessed_docs = [preprocess_text(doc, nlp) for doc in documents]
    
    # Perform TF-IDF, PCA, LSA, and t-SNE with reduced components
    pca_result, lsa_result, tsne_result, vectorizer, pca, lsa, tsne = perform_tfidf_and_dim_reduction(
        preprocessed_docs, 
        n_components=min(30, len(documents) - 1)  # Use 30 or one less than the number of documents, whichever is smaller
    )
    
    if vectorizer is None:
        logger.error("TF-IDF vectorization failed. Cannot proceed with visualization.")
        return

    tfidf_matrix = vectorizer.fit_transform(preprocessed_docs)

    # Group 1: Dimension Reduction Visualizations
    dimension_reduction_plots = [
        (pca_result, "PCA of Document Semantics", "pca_plot.png", "PCA", pca),
        (lsa_result, "LSA of Document Semantics", "lsa_plot.png", "LSA", lsa),
        (tsne_result, "t-SNE of Document Semantics", "tsne_plot.png", "t-SNE", tsne)
    ]

    for result, title, filename, method, model in dimension_reduction_plots:
        if result is not None:
            try:
                plot_dimension_reduction(result, filenames, labels, title, filename, method, vectorizer, model, output_folder)
            except Exception as e:
                logger.error(f"Error creating {title} plot: {str(e)}")
        else:
            logger.error(f"{method} failed. Cannot create {title} plot.")

    # Enhanced PCA Visualizations
    if pca_result is not None:
        try:
            organizations, recipients, _ = zip(*[extract_prompt_info(filename) for filename in filenames])
            
            color_schemes = [
                ('Organization', organizations),
                ('Recipient', recipients),
                ('Label', labels)
            ]
            
            for scheme_name, scheme_values in color_schemes:
                plot_dimension_reduction(pca_result, filenames, scheme_values, 
                                         f"PCA colored by {scheme_name}", 
                                         f"pca_plot_{scheme_name.lower().replace(' ', '_')}.png", 
                                         "PCA", vectorizer, pca, output_folder)
            
            plot_pca_scree(pca, output_folder)
            plot_pca_cumulative_variance(pca, output_folder)
            plot_pca_loadings_heatmap(pca, vectorizer, output_folder)
            save_pca_top_features(pca, vectorizer, output_folder)
            plot_pca_3d(pca_result, labels, output_folder)
        except Exception as e:
            logger.error(f"Error in enhanced PCA visualizations: {str(e)}")
    else:
        logger.error("PCA failed. Cannot create PCA plots.")

    # Group 2: Word Importance and PCA Visualizations
    try:
        plot_word_importance(vectorizer, pca, "Word Importance (PCA)", "word_importance_pca.png", output_folder)
        plot_word_importance(vectorizer, lsa, "Word Importance (LSA)", "word_importance_lsa.png", output_folder)
        plot_pca_eigen_terms(vectorizer, pca, "PCA Eigen Terms and Components", "pca_eigen_terms.png", output_folder)
    except Exception as e:
        logger.error(f"Error in word importance or PCA visualizations: {str(e)}")

    # Group 3: Text Analysis Visualizations
    text_analysis_plots = [
        (create_word_cloud, (preprocessed_docs,), "Word Cloud of All Documents", "word_cloud.png"),
        (plot_prompt_distribution, (filenames, organizations, recipients), "Organization and Recipient Distribution", "prompt_distribution.png"),
        (plot_topic_modeling, (vectorizer, tfidf_matrix), "LDA Topic Modeling", "lda_topics.png"),
        (plot_heatmap, (vectorizer, tfidf_matrix, filenames), "TF-IDF Heatmap of Top Terms", "tfidf_heatmap.png"),
        (plot_confidence_intervals, (vectorizer, tfidf_matrix, filenames), "Confidence Intervals for Top Terms", "confidence_intervals.png"),
        (plot_system_prompt_comparison, (filenames, preprocessed_docs), "System Prompt Comparison", "system_prompt_comparison.png"),
        (plot_term_frequency_distribution, (preprocessed_docs,), "Term Frequency Distribution", "term_frequency_distribution.png"),
        (plot_term_network, (vectorizer, tfidf_matrix), "Term Co-occurrence Network", "term_network.png")
    ]

    for plot_func, args, title, filename in text_analysis_plots:
        try:
            plot_func(*args, title, filename, output_folder)
        except Exception as e:
            logger.error(f"Error creating {title} plot: {str(e)}")

    logger.info(f"Semantic analysis completed. Plots saved in {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform semantic analysis on markdown files.")
    parser.add_argument("--input", help="Path to the input folder containing markdown files.")
    parser.add_argument("--output", default="Visualizations/", help="Path to the output folder for visualizations.")
    args = parser.parse_args()

    if args.input:
        INPUT_FOLDER = args.input
    else:
        # Try to find the Introductions folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        INPUT_FOLDER = find_introductions_folder(project_root)
        if not INPUT_FOLDER:
            logger.error("Could not find the 'Introductions' folder. Please specify the input folder using --input.")
            sys.exit(1)

    OUTPUT_FOLDER = args.output

    main(INPUT_FOLDER, OUTPUT_FOLDER)
