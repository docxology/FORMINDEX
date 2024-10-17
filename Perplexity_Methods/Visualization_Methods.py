import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD, LatentDirichletAllocation
from sklearn.manifold import TSNE
from nltk.corpus import stopwords
import logging
from typing import List, Tuple, Union
import re
from wordcloud import WordCloud
from collections import Counter
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
import networkx as nx
from networkx.algorithms import community

logger = logging.getLogger(__name__)

def read_markdown_files(folder_path: str) -> Tuple[List[str], List[str], List[str]]:
    """Read all Markdown files in the given folder and its subfolders."""
    documents = []
    filenames = []
    labels = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(content)
                        filenames.append(file)
                        labels.append(os.path.relpath(root, folder_path))
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {str(e)}")
    
    return documents, filenames, labels

def preprocess_text(text: str, nlp) -> str:
    """Preprocess the text by tokenizing, removing stopwords, and lemmatizing."""
    try:
        stop_words = set(stopwords.words('english'))
        doc = nlp(text.lower())
        tokens = [token.lemma_ for token in doc if token.text not in stop_words and token.is_alpha]
        return ' '.join(tokens)
    except Exception as e:
        logger.error(f"Error preprocessing text: {str(e)}")
        return ""

def extract_prompt_info(filename: str) -> Tuple[str, str, str]:
    """Extract System prompt and User prompt from the filename."""
    try:
        match = re.search(r'Prompt_S(\d+)_(.+?)_U_(.+)_\d+\.md', filename)
        if match:
            system_prompt_id = match.group(1)
            system_prompt_label = match.group(2).replace('_', ' ')
            system_prompt = f"S{system_prompt_id} {system_prompt_label}"
            user_prompt = match.group(3).replace('_', ' ')
            return system_prompt, system_prompt_label, user_prompt
        return "Unknown", "Unknown", "Unknown"
    except Exception as e:
        logger.error(f"Error extracting prompt info from filename {filename}: {str(e)}")
        return "Unknown", "Unknown", "Unknown"

def perform_tfidf_and_dim_reduction(documents: List[str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, TfidfVectorizer, PCA, TruncatedSVD, TSNE]:
    """Perform TF-IDF vectorization, PCA, LSA, and t-SNE on the documents."""
    try:
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        n_components = min(5, tfidf_matrix.shape[1] - 1)
        
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(tfidf_matrix.toarray())
        
        lsa = TruncatedSVD(n_components=n_components, random_state=42)
        lsa_result = lsa.fit_transform(tfidf_matrix)
        
        tsne = TSNE(n_components=3, random_state=42)  # Increase to 3D
        tsne_result = tsne.fit_transform(tfidf_matrix.toarray())
        
        logger.info("TF-IDF vectorization, PCA, LSA, and t-SNE completed successfully.")
        return pca_result, lsa_result, tsne_result, vectorizer, pca, lsa, tsne
    except Exception as e:
        logger.error(f"Error during TF-IDF vectorization or dimension reduction: {str(e)}")
        return None, None, None, None, None, None, None

def plot_dimension_reduction(result: np.ndarray, filenames: List[str], 
                             title: str, output_filename: str, method: str,
                             vectorizer: TfidfVectorizer, dim_reduction, output_folder: str) -> None:
    try:
        fig, ax = plt.subplots(figsize=(20, 16))
        
        # Plot the points
        scatter = ax.scatter(result[:, 0], result[:, 1], alpha=0.7)
        
        # Add labels for some points (e.g., every 10th point)
        for i in range(0, len(filenames), 10):
            ax.annotate(filenames[i][:20], (result[i, 0], result[i, 1]), fontsize=8)
        
        ax.set_title(title, fontsize=24)
        ax.set_xlabel(f'{method} Component 1', fontsize=18)
        ax.set_ylabel(f'{method} Component 2', fontsize=18)
        
        # Add top terms for each component
        feature_names = vectorizer.get_feature_names_out()
        if isinstance(dim_reduction, (PCA, TruncatedSVD)):
            components = dim_reduction.components_
            for i, comp in enumerate(['x', 'y']):
                if i < components.shape[0]:
                    top_features = feature_names[components[i].argsort()[-5:]]
                    ax.text(0.05, 0.95-i*0.05, f"{comp}-axis top terms: {', '.join(top_features)}", 
                            transform=ax.transAxes, fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating {title} plot: {str(e)}")
        logger.debug(f"Result shape: {result.shape}, Number of filenames: {len(filenames)}")
        logger.debug(f"Type of dim_reduction: {type(dim_reduction)}")

def plot_word_importance(vectorizer: TfidfVectorizer, dim_reduction: Union[PCA, TruncatedSVD], 
                         title: str, output_filename: str, output_folder: str) -> None:
    try:
        feature_names = vectorizer.get_feature_names_out()
        loadings = dim_reduction.components_.T
        n_components = loadings.shape[1]
        
        fig = plt.figure(figsize=(30, 6 * n_components))
        gs = gridspec.GridSpec(n_components, 2, width_ratios=[3, 1])
        
        for i in range(n_components):
            component = loadings[:, i]
            sorted_idx = component.argsort()
            top_features = feature_names[sorted_idx[-20:]]
            top_weights = component[sorted_idx[-20:]]
            
            ax_bar = fig.add_subplot(gs[i, 0])
            ax_bar.barh(top_features, top_weights, height=0.8, edgecolor='black')
            ax_bar.set_title(f'Top 20 words for component {i+1}', fontsize=24)
            ax_bar.set_xlabel('Weight', fontsize=20)
            ax_bar.set_ylabel('Words', fontsize=20)
            ax_bar.tick_params(axis='both', which='major', labelsize=16)
            
            ax_cloud = fig.add_subplot(gs[i, 1])
            wordcloud = WordCloud(width=400, height=200, background_color='white').generate_from_frequencies(
                dict(zip(top_features, top_weights))
            )
            ax_cloud.imshow(wordcloud, interpolation='bilinear')
            ax_cloud.axis('off')
            ax_cloud.set_title(f'Word Cloud for component {i+1}', fontsize=20)
        
        plt.suptitle(title, fontsize=32, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating word importance plot: {str(e)}")

def plot_pca_eigen_terms(vectorizer: TfidfVectorizer, pca: PCA, 
                         title: str, output_filename: str, output_folder: str) -> None:
    try:
        feature_names = vectorizer.get_feature_names_out()
        n_components = pca.n_components_
        
        fig = plt.figure(figsize=(30, 20))
        gs = gridspec.GridSpec(2, 2)
        
        # 2D plots
        ax_2d = fig.add_subplot(gs[0, 0])
        for i in range(n_components):
            eigen_vector = pca.components_[i]
            sorted_idx = eigen_vector.argsort()
            top_terms = feature_names[sorted_idx[-10:]]
            top_weights = eigen_vector[sorted_idx[-10:]]
            
            ax_2d.barh(top_terms, top_weights, height=0.8, label=f'Component {i+1}', edgecolor='black')
        
        ax_2d.set_title('Top 10 eigen terms for PCA components', fontsize=24)
        ax_2d.set_xlabel('Weight', fontsize=20)
        ax_2d.set_ylabel('Terms', fontsize=20)
        ax_2d.tick_params(axis='both', which='major', labelsize=16)
        ax_2d.legend(fontsize=16)
        
        # 3D plot
        ax_3d = fig.add_subplot(gs[0, 1], projection='3d')
        colors = cm.rainbow(np.linspace(0, 1, n_components))
        
        for i, color in zip(range(n_components), colors):
            eigen_vector = pca.components_[i]
            sorted_idx = eigen_vector.argsort()
            top_terms = feature_names[sorted_idx[-10:]]
            top_weights = eigen_vector[sorted_idx[-10:]]
            
            ax_3d.bar(top_terms, top_weights, zs=i, zdir='y', color=color, alpha=0.8)
        
        ax_3d.set_xlabel('Terms', fontsize=16)
        ax_3d.set_ylabel('Components', fontsize=16)
        ax_3d.set_zlabel('Weights', fontsize=16)
        ax_3d.set_title('3D visualization of PCA components', fontsize=24)
        
        # Eigenvalue plot
        ax_eigen = fig.add_subplot(gs[1, 0])
        eigenvalues = pca.explained_variance_ratio_
        ax_eigen.plot(range(1, len(eigenvalues) + 1), eigenvalues, 'bo-')
        ax_eigen.set_xlabel('Principal Component', fontsize=20)
        ax_eigen.set_ylabel('Proportion of Variance Explained', fontsize=20)
        ax_eigen.set_title('Scree Plot', fontsize=24)
        
        # Cumulative variance plot
        ax_cumulative = fig.add_subplot(gs[1, 1])
        cumulative_variance = np.cumsum(eigenvalues)
        ax_cumulative.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'ro-')
        ax_cumulative.set_xlabel('Number of Components', fontsize=20)
        ax_cumulative.set_ylabel('Cumulative Proportion of Variance Explained', fontsize=20)
        ax_cumulative.set_title('Cumulative Variance Plot', fontsize=24)
        
        plt.suptitle(title, fontsize=32, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating PCA eigen terms plot: {str(e)}")

def create_word_cloud(documents: List[str], title: str, output_filename: str, output_folder: str) -> None:
    try:
        text = ' '.join(documents)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=24)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} word cloud saved successfully.")
    except Exception as e:
        logger.error(f"Error creating word cloud: {str(e)}")

def plot_prompt_distribution(filenames: List[str], title: str, output_filename: str, output_folder: str) -> None:
    try:
        system_prompts, _, user_prompts = zip(*[extract_prompt_info(filename) for filename in filenames])
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 16))
        
        # System Prompts distribution
        sns.countplot(y=system_prompts, ax=ax1, order=sorted(set(system_prompts)))
        ax1.set_title('Distribution of System Prompts', fontsize=18)
        ax1.set_xlabel('Count', fontsize=14)
        ax1.set_ylabel('System Prompt', fontsize=14)
        
        # User Prompts word frequency
        user_prompt_words = ' '.join(user_prompts).split()
        word_freq = Counter(user_prompt_words).most_common(20)
        words, counts = zip(*word_freq)
        sns.barplot(x=list(counts), y=list(words), ax=ax2)
        ax2.set_title('Top 20 Words in User Prompts', fontsize=18)
        ax2.set_xlabel('Frequency', fontsize=14)
        ax2.set_ylabel('Word', fontsize=14)
        
        plt.suptitle(title, fontsize=24)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating prompt distribution plot: {str(e)}")

def plot_topic_modeling(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                        title: str, output_filename: str, output_folder: str, n_topics: int = 5) -> None:
    try:
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(tfidf_matrix)
        
        feature_names = vectorizer.get_feature_names_out()
        
        plt.figure(figsize=(25, 5 * n_topics))
        for topic_idx, topic in enumerate(lda.components_):
            top_features_idx = topic.argsort()[:-10 - 1:-1]
            top_features = [feature_names[i] for i in top_features_idx]
            weights = topic[top_features_idx]
            
            plt.subplot(n_topics, 1, topic_idx + 1)
            plt.barh(top_features, weights)
            plt.title(f'Topic {topic_idx + 1}', fontsize=22)
            plt.xlabel('Weight', fontsize=18)
            plt.ylabel('Terms', fontsize=18)
            plt.tick_params(axis='both', which='major', labelsize=14)
        
        plt.suptitle(title, fontsize=28)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating topic modeling plot: {str(e)}")

def plot_heatmap(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                 filenames: List[str], title: str, output_filename: str, output_folder: str) -> None:
    try:
        feature_names = vectorizer.get_feature_names_out()
        n_top_words = 50
        top_tfidf_indices = tfidf_matrix.sum(axis=0).argsort()[0, -n_top_words:].A1
        top_tfidf_terms = [feature_names[i] for i in top_tfidf_indices]
        
        heatmap_data = tfidf_matrix[:, top_tfidf_indices].toarray()
        
        plt.figure(figsize=(20, 15))
        sns.heatmap(heatmap_data, xticklabels=top_tfidf_terms, yticklabels=[f"Doc {i+1}" for i in range(len(filenames))],
                    cmap="YlOrRd", cbar_kws={'label': 'TF-IDF Score'})
        plt.title(title, fontsize=16)
        plt.xlabel("Top Terms", fontsize=12)
        plt.ylabel("Documents", fontsize=12)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} heatmap saved successfully.")
    except Exception as e:
        logger.error(f"Error creating heatmap: {str(e)}")
        logger.debug(f"TF-IDF matrix shape: {tfidf_matrix.shape}, Number of filenames: {len(filenames)}")

def plot_confidence_intervals(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                              filenames: List[str], title: str, output_filename: str, output_folder: str) -> None:
    try:
        feature_names = vectorizer.get_feature_names_out()
        n_top_words = 20
        top_tfidf_indices = tfidf_matrix.sum(axis=0).argsort()[0, -n_top_words:].A1
        top_tfidf_terms = [feature_names[i] for i in top_tfidf_indices]
        
        ci_data = tfidf_matrix[:, top_tfidf_indices].toarray()
        
        means = np.mean(ci_data, axis=0)
        stds = np.std(ci_data, axis=0)
        cis = stats.t.interval(0.95, len(filenames)-1, loc=means, scale=stds/np.sqrt(len(filenames)))
        
        plt.figure(figsize=(15, 10))
        plt.errorbar(top_tfidf_terms, means, yerr=cis[1]-means, fmt='o', capsize=5)
        plt.title(title, fontsize=16)
        plt.xlabel("Top Terms", fontsize=12)
        plt.ylabel("Mean TF-IDF Score", fontsize=12)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} confidence intervals plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating confidence intervals plot: {str(e)}")
        logger.debug(f"TF-IDF matrix shape: {tfidf_matrix.shape}, Number of filenames: {len(filenames)}")

def plot_system_prompt_comparison(filenames: List[str], preprocessed_docs: List[str], 
                                  title: str, output_filename: str, output_folder: str) -> None:
    try:
        system_prompts, _, _ = zip(*[extract_prompt_info(filename) for filename in filenames])
        unique_prompts = sorted(set(system_prompts))
        
        # Calculate document lengths
        doc_lengths = [len(doc.split()) for doc in preprocessed_docs]
        
        # Prepare data for statistical tests and plotting
        data = {prompt: [] for prompt in unique_prompts}
        for prompt, length in zip(system_prompts, doc_lengths):
            data[prompt].append(length)
        
        # Perform t-tests
        t_test_results = {}
        for i, prompt1 in enumerate(unique_prompts):
            for prompt2 in unique_prompts[i+1:]:
                t_stat, p_value = stats.ttest_ind(data[prompt1], data[prompt2])
                t_test_results[f"{prompt1} vs {prompt2}"] = p_value
        
        # Perform one-way ANOVA
        f_statistic, p_value = stats.f_oneway(*data.values())
        
        # Create a color map for system prompts
        color_map = plt.cm.get_cmap('tab20')
        color_dict = {prompt: color_map(i/len(unique_prompts)) for i, prompt in enumerate(unique_prompts)}
        
        # Plot
        plt.figure(figsize=(30, 25))  # Increase figure size
        sns.boxplot(x=[prompt for prompt in data.keys() for _ in data[prompt]], 
                    y=[length for lengths in data.values() for length in lengths],
                    hue=[prompt for prompt in data.keys() for _ in data[prompt]],
                    palette=color_dict,
                    legend=False)
        plt.title(title, fontsize=20)  # Reduce font size
        plt.xlabel("System Prompt", fontsize=16)
        plt.ylabel("Document Length", fontsize=16)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        
        # Add statistical test results to the plot
        plt.text(0.05, 0.95, f"ANOVA: F={f_statistic:.4f}, p={p_value:.4f}", 
                 transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
        y_max = max([max(lengths) for lengths in data.values()])
        y_increment = y_max * 0.05
        for i, (comparison, p_value) in enumerate(t_test_results.items()):
            plt.text(0.05, 0.9 - i*0.03, f"{comparison}: p={p_value:.4f}", 
                     transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} system prompt comparison plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating system prompt comparison plot: {str(e)}")
        logger.debug(f"Number of filenames: {len(filenames)}, Number of preprocessed docs: {len(preprocessed_docs)}")

def plot_term_frequency_distribution(preprocessed_docs: List[str], 
                                     title: str, output_filename: str, output_folder: str) -> None:
    try:
        # Calculate term frequencies
        all_terms = ' '.join(preprocessed_docs).split()
        term_freq = Counter(all_terms)
        
        # Get top 100 terms
        top_terms = dict(term_freq.most_common(100))
        
        plt.figure(figsize=(15, 10))
        plt.bar(top_terms.keys(), top_terms.values())
        plt.title(title, fontsize=16)
        plt.xlabel("Terms", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.xticks(rotation=90)
        plt.yscale('log')  # Use log scale for better visualization
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} term frequency distribution plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating term frequency distribution plot: {str(e)}")

def plot_term_network(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                      title: str, output_filename: str, output_folder: str, n_terms: int = 50, threshold: float = 0.3) -> None:
    try:
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top n terms based on TF-IDF scores
        tfidf_sum = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
        top_term_indices = tfidf_sum.argsort()[-n_terms:][::-1]
        top_terms = [feature_names[i] for i in top_term_indices]
        
        # Create term-term correlation matrix
        term_term_matrix = np.corrcoef(tfidf_matrix[:, top_term_indices].toarray().T)
        
        # Create graph
        G = nx.Graph()
        for i, term1 in enumerate(top_terms):
            for j, term2 in enumerate(top_terms[i+1:], start=i+1):
                correlation = term_term_matrix[i, j]
                if correlation > threshold:
                    G.add_edge(term1, term2, weight=correlation)
        
        if len(G.nodes()) == 0:
            logger.warning("No connections found between terms above the threshold. The graph is empty.")
            return
        
        # Compute communities
        communities = community.greedy_modularity_communities(G)
        
        # Assign colors to communities
        color_map = plt.cm.get_cmap('tab20')
        colors = [color_map(i / len(communities)) for i in range(len(communities))]
        
        # Assign nodes to communities
        node_colors = []
        for node in G.nodes():
            for i, comm in enumerate(communities):
                if node in comm:
                    node_colors.append(colors[i])
                    break
        
        # Calculate node sizes based on degree centrality
        centrality = nx.degree_centrality(G)
        node_sizes = [centrality[node] * 5000 for node in G.nodes()]
        
        # Plot
        plt.figure(figsize=(20, 20))
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Draw edges with varying thickness based on weight
        edge_weights = [G[u][v]['weight'] * 2 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.3, edge_color='gray')
        
        plt.title(title, fontsize=24)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} term network plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating term network plot: {str(e)}")
        logger.debug(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

def plot_pca_scree(pca, output_folder: str) -> None:
    plt.figure(figsize=(12, 8))
    plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), pca.explained_variance_ratio_, 'bo-')
    plt.title('Scree Plot: Explained Variance Ratio by PCA Component')
    plt.xlabel('Principal Component')
    plt.ylabel('Explained Variance Ratio')
    plt.savefig(os.path.join(output_folder, 'pca_scree_plot.png'))
    plt.close()
    logger.info("PCA scree plot saved successfully.")

def plot_pca_cumulative_variance(pca, output_folder: str) -> None:
    plt.figure(figsize=(12, 8))
    plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), np.cumsum(pca.explained_variance_ratio_), 'ro-')
    plt.title('Cumulative Explained Variance Ratio')
    plt.xlabel('Number of Components')
    plt.ylabel('Cumulative Explained Variance Ratio')
    plt.savefig(os.path.join(output_folder, 'pca_cumulative_variance.png'))
    plt.close()
    logger.info("PCA cumulative variance plot saved successfully.")

def plot_pca_loadings_heatmap(pca, vectorizer, output_folder: str) -> None:
    plt.figure(figsize=(20, 12))
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f'PC{i}' for i in range(1, pca.n_components_ + 1)],
        index=vectorizer.get_feature_names_out()
    )
    plt.imshow(loadings, cmap='coolwarm', aspect='auto')
    plt.colorbar()
    plt.title('PCA Loadings Heatmap')
    plt.xlabel('Principal Components')
    plt.ylabel('Features')
    plt.savefig(os.path.join(output_folder, 'pca_loadings_heatmap.png'))
    plt.close()
    logger.info("PCA loadings heatmap saved successfully.")

def save_pca_top_features(pca, vectorizer, output_folder: str) -> None:
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f'PC{i}' for i in range(1, pca.n_components_ + 1)],
        index=vectorizer.get_feature_names_out()
    )
    top_features = pd.DataFrame(
        {f'PC{i+1}': loadings.iloc[:, i].abs().nlargest(10).index.tolist()
         for i in range(pca.n_components_)}
    )
    top_features.to_csv(os.path.join(output_folder, 'pca_top_features.csv'), index=False)
    logger.info("PCA top features saved successfully.")

def plot_pca_3d(pca_result, labels, output_folder: str) -> None:
    if pca_result.shape[1] >= 3:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Convert labels to numeric values for coloring
        unique_labels = list(set(labels))
        label_to_num = {label: i for i, label in enumerate(unique_labels)}
        numeric_labels = [label_to_num[label] for label in labels]
        
        scatter = ax.scatter(pca_result[:, 0], pca_result[:, 1], pca_result[:, 2], c=numeric_labels, cmap='viridis')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_zlabel('PC3')
        plt.colorbar(scatter, label='Label', ticks=range(len(unique_labels)), format=plt.FuncFormatter(lambda val, loc: unique_labels[int(val)]))
        plt.title('3D PCA Visualization')
        plt.savefig(os.path.join(output_folder, 'pca_3d_plot.png'))
        plt.close()
        logger.info("3D PCA plot saved successfully.")
    else:
        logger.warning("Not enough components for 3D PCA plot.")