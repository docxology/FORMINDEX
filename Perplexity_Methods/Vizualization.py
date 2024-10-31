import os
import sys
import logging
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

# Input and output folder specifications
INPUT_FOLDER = "Markdown_Output/"
OUTPUT_FOLDER = "Visualizations/"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Failed to load spaCy model: {str(e)}")
    sys.exit(1)

def main() -> None:
    logger.info(f"Starting semantic analysis for folder: {INPUT_FOLDER}")
    
    if not os.path.isdir(INPUT_FOLDER):
        logger.error(f"The specified input path is not a valid directory: {INPUT_FOLDER}")
        return
    
    # Read documents
    documents, filenames, labels = read_markdown_files(INPUT_FOLDER)
    
    if not documents:
        logger.warning("No markdown files found in the specified directory.")
        return
    
    logger.info(f"Found {len(documents)} markdown files.")
    
    # Preprocess documents
    preprocessed_docs = [preprocess_text(doc, nlp) for doc in documents]
    
    # Perform TF-IDF, PCA, LSA, and t-SNE
    pca_result, lsa_result, tsne_result, vectorizer, pca, lsa, tsne = perform_tfidf_and_dim_reduction(preprocessed_docs)
    
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
                plot_dimension_reduction(result, filenames, title, filename, method, vectorizer, model, OUTPUT_FOLDER)
            except Exception as e:
                logger.error(f"Error creating {title} plot: {str(e)}")
        else:
            logger.error(f"{method} failed. Cannot create {title} plot.")

    # Enhanced PCA Visualizations
    if pca_result is not None:
        try:
            system_prompts, _, user_prompts = zip(*[extract_prompt_info(filename) for filename in filenames])
            
            color_schemes = [
                ('System Prompt', system_prompts),
                ('User Prompt', user_prompts),
                ('Label', labels)
            ]
            
            for scheme_name, scheme_values in color_schemes:
                plot_dimension_reduction(pca_result, filenames, 
                                         f"PCA colored by {scheme_name}", 
                                         f"pca_plot_{scheme_name.lower().replace(' ', '_')}.png", 
                                         "PCA", vectorizer, pca, OUTPUT_FOLDER)
            
            plot_pca_scree(pca, OUTPUT_FOLDER)
            plot_pca_cumulative_variance(pca, OUTPUT_FOLDER)
            plot_pca_loadings_heatmap(pca, vectorizer, OUTPUT_FOLDER)
            save_pca_top_features(pca, vectorizer, OUTPUT_FOLDER)
            plot_pca_3d(pca_result, labels, OUTPUT_FOLDER)
        except Exception as e:
            logger.error(f"Error in enhanced PCA visualizations: {str(e)}")
    else:
        logger.error("PCA failed. Cannot create PCA plots.")

    # Group 2: Word Importance and PCA Visualizations
    try:
        plot_word_importance(vectorizer, pca, "Word Importance (PCA)", "word_importance_pca.png", OUTPUT_FOLDER)
        plot_word_importance(vectorizer, lsa, "Word Importance (LSA)", "word_importance_lsa.png", OUTPUT_FOLDER)
        plot_pca_eigen_terms(vectorizer, pca, "PCA Eigen Terms and Components", "pca_eigen_terms.png", OUTPUT_FOLDER)
    except Exception as e:
        logger.error(f"Error in word importance or PCA visualizations: {str(e)}")

    # Group 3: Text Analysis Visualizations
    text_analysis_plots = [
        (create_word_cloud, (preprocessed_docs,), "Word Cloud of All Documents", "word_cloud.png"),
        (plot_prompt_distribution, (filenames,), "Prompt Distribution and User Prompt Word Frequency", "prompt_distribution.png"),
        (plot_topic_modeling, (vectorizer, tfidf_matrix), "LDA Topic Modeling", "lda_topics.png"),
        (plot_heatmap, (vectorizer, tfidf_matrix, filenames), "TF-IDF Heatmap of Top Terms", "tfidf_heatmap.png"),
        (plot_confidence_intervals, (vectorizer, tfidf_matrix, filenames), "Confidence Intervals for Top Terms", "confidence_intervals.png"),
        (plot_system_prompt_comparison, (filenames, preprocessed_docs), "System Prompt Comparison", "system_prompt_comparison.png"),
        (plot_term_frequency_distribution, (preprocessed_docs,), "Term Frequency Distribution", "term_frequency_distribution.png"),
        (plot_term_network, (vectorizer, tfidf_matrix), "Term Co-occurrence Network", "term_network.png")
    ]

    for plot_func, args, title, filename in text_analysis_plots:
        try:
            plot_func(*args, title, filename, OUTPUT_FOLDER)
        except Exception as e:
            logger.error(f"Error creating {title} plot: {str(e)}")

    logger.info(f"Semantic analysis completed. Plots saved in {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()
