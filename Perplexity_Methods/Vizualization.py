import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from nltk.corpus import stopwords
import spacy
import logging
from typing import List, Tuple, Union
import re
from wordcloud import WordCloud
from collections import Counter
import matplotlib.cm as cm
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import networkx as nx
from networkx.algorithms import community

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

def preprocess_text(text: str) -> str:
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
        
        # Increase the number of components
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

def plot_dimension_reduction(result: np.ndarray, filenames: List[str], labels: List[str], 
                             title: str, output_filename: str, method: str,
                             vectorizer: TfidfVectorizer, dim_reduction) -> None:
    """Plot dimension reduction results with improved visuals and axis semantics."""
    try:
        fig = plt.figure(figsize=(30, 24))
        gs = gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[3, 1])
        
        # Main scatter plot
        ax_main = fig.add_subplot(gs[0, 0], projection='3d' if result.shape[1] == 3 else None)
        
        # Extract prompt information
        system_prompts, _, user_prompts = zip(*[extract_prompt_info(filename) for filename in filenames])
        
        # Create a DataFrame
        df = pd.DataFrame({
            'x': result[:, 0],
            'y': result[:, 1],
            'z': result[:, 2] if result.shape[1] == 3 else np.zeros(len(result)),
            'System_Prompt': system_prompts,
            'User_Prompt': user_prompts,
            'Label': labels
        })
        
        # Plot points with increased size and edge color
        scatter = ax_main.scatter(df['x'], df['y'], df['z'], 
                                  c=pd.factorize(df['System_Prompt'])[0], 
                                  edgecolor='black', 
                                  linewidth=1, 
                                  cmap='viridis')
        
        # Improve readability
        ax_main.set_title(title, fontsize=36, fontweight='bold')
        ax_main.set_xlabel(f'{method} Component 1', fontsize=28)
        ax_main.set_ylabel(f'{method} Component 2', fontsize=28)
        if result.shape[1] == 3:
            ax_main.set_zlabel(f'{method} Component 3', fontsize=28)
        ax_main.tick_params(axis='both', which='major', labelsize=20)
        
        # Add colorbar legend
        cbar = plt.colorbar(scatter, ax=ax_main, pad=0.1)
        cbar.set_label('System Prompt', fontsize=24)
        cbar.ax.tick_params(labelsize=20)
        
        # Add annotations for user prompts (limited to avoid clutter)
        for idx, row in df.iloc[::5].iterrows():  # Annotate every 5th point
            ax_main.text(row['x'], row['y'], row['z'], row['User_Prompt'][:20] + '...', 
                         fontsize=14, alpha=0.7)
        
        # Highlight semantics of the axes
        feature_names = vectorizer.get_feature_names_out()
        if hasattr(dim_reduction, 'components_'):
            for i, comp in enumerate(['x', 'y', 'z']):
                if i < dim_reduction.components_.shape[0]:
                    top_features = feature_names[dim_reduction.components_[i].argsort()[-5:]]
                    ax_main.text2D(0.05, 0.95-i*0.05, f"{comp.upper()}-axis top terms: {', '.join(top_features)}", 
                                   transform=ax_main.transAxes, fontsize=20)
        
        # Add histograms
        ax_histx = fig.add_subplot(gs[1, 0], sharex=ax_main)
        ax_histy = fig.add_subplot(gs[0, 1], sharey=ax_main)
        
        ax_histx.hist(df['x'], bins=50, edgecolor='black')
        ax_histy.hist(df['y'], bins=50, orientation='horizontal', edgecolor='black')
        
        ax_histx.set_title('Distribution of Component 1', fontsize=22)
        ax_histy.set_title('Distribution of Component 2', fontsize=22)
        
        # Remove labels on shared axes
        ax_histx.tick_params(axis="x", labelbottom=False)
        ax_histy.tick_params(axis="y", labelleft=False)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating {title} plot: {str(e)}")

def plot_word_importance(vectorizer: TfidfVectorizer, dim_reduction: Union[PCA, TruncatedSVD], 
                         title: str, output_filename: str) -> None:
    """Plot word importance based on PCA or LSA loadings."""
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
            
            # Add word cloud for each component
            ax_cloud = fig.add_subplot(gs[i, 1])
            wordcloud = WordCloud(width=400, height=200, background_color='white').generate_from_frequencies(
                dict(zip(top_features, top_weights))
            )
            ax_cloud.imshow(wordcloud, interpolation='bilinear')
            ax_cloud.axis('off')
            ax_cloud.set_title(f'Word Cloud for component {i+1}', fontsize=20)
        
        plt.suptitle(title, fontsize=32, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating word importance plot: {str(e)}")

def plot_pca_eigen_terms(vectorizer: TfidfVectorizer, pca: PCA, 
                         title: str, output_filename: str) -> None:
    """Plot PCA eigen terms and topics with 3D visualization."""
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
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating PCA eigen terms plot: {str(e)}")

def create_word_cloud(documents: List[str], title: str, output_filename: str) -> None:
    """Create and save a word cloud from the documents."""
    try:
        text = ' '.join(documents)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=24)
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} word cloud saved successfully.")
    except Exception as e:
        logger.error(f"Error creating word cloud: {str(e)}")

def plot_prompt_distribution(filenames: List[str], title: str, output_filename: str) -> None:
    """Plot the distribution of system prompts and user prompts."""
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
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating prompt distribution plot: {str(e)}")

def plot_topic_modeling(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                        title: str, output_filename: str, n_topics: int = 5) -> None:
    """Perform LDA topic modeling and plot results."""
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
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating topic modeling plot: {str(e)}")

def plot_heatmap(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                 filenames: List[str], title: str, output_filename: str) -> None:
    """Plot a heatmap of TF-IDF values for top terms across documents."""
    try:
        feature_names = vectorizer.get_feature_names_out()
        n_top_words = 50
        top_tfidf_indices = tfidf_matrix.sum(axis=0).argsort()[0, -n_top_words:]
        top_tfidf_terms = [feature_names[i] for i in top_tfidf_indices.tolist()[0]]
        
        heatmap_data = tfidf_matrix[:, top_tfidf_indices].toarray().squeeze()
        
        plt.figure(figsize=(20, 15))
        sns.heatmap(heatmap_data, xticklabels=top_tfidf_terms, yticklabels=[f"Doc {i+1}" for i in range(len(filenames))],
                    cmap="YlOrRd", cbar_kws={'label': 'TF-IDF Score'})
        plt.title(title, fontsize=16)
        plt.xlabel("Top Terms", fontsize=12)
        plt.ylabel("Documents", fontsize=12)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} heatmap saved successfully.")
    except Exception as e:
        logger.error(f"Error creating heatmap: {str(e)}")

def plot_confidence_intervals(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                              filenames: List[str], title: str, output_filename: str) -> None:
    """Plot confidence intervals for top terms across documents."""
    try:
        feature_names = vectorizer.get_feature_names_out()
        n_top_words = 20
        top_tfidf_indices = tfidf_matrix.sum(axis=0).argsort()[0, -n_top_words:]
        top_tfidf_terms = [feature_names[i] for i in top_tfidf_indices.tolist()[0]]
        
        ci_data = tfidf_matrix[:, top_tfidf_indices].toarray().squeeze()
        
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
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} confidence intervals plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating confidence intervals plot: {str(e)}")

def plot_system_prompt_comparison(filenames: List[str], preprocessed_docs: List[str], 
                                  title: str, output_filename: str) -> None:
    """Plot a bar chart comparing system prompts with t-tests and ANOVA."""
    try:
        system_prompts, _, _ = zip(*[extract_prompt_info(filename) for filename in filenames])
        unique_prompts = list(set(system_prompts))
        
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
        
        # Plot
        plt.figure(figsize=(25, 20))  # Increase figure size
        sns.boxplot(x=[prompt for prompt in data.keys() for _ in data[prompt]], 
                    y=[length for lengths in data.values() for length in lengths])
        plt.title(title, fontsize=24)
        plt.xlabel("System Prompt", fontsize=20)
        plt.ylabel("Document Length", fontsize=20)
        plt.xticks(rotation=45, ha='right', fontsize=16)
        plt.yticks(fontsize=16)
        
        # Add statistical test results to the plot
        plt.text(0.05, 0.95, f"ANOVA: F={f_statistic:.4f}, p={p_value:.4f}", 
                 transform=plt.gca().transAxes, fontsize=16, verticalalignment='top')
        y_max = max([max(lengths) for lengths in data.values()])
        y_increment = y_max * 0.05
        for i, (comparison, p_value) in enumerate(t_test_results.items()):
            plt.text(0.05, 0.9 - i*0.05, f"{comparison}: p={p_value:.4f}", 
                     transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the rect parameter
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} system prompt comparison plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating system prompt comparison plot: {str(e)}")

def plot_term_frequency_distribution(preprocessed_docs: List[str], 
                                     title: str, output_filename: str) -> None:
    """Plot the distribution of term frequencies across documents."""
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
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} term frequency distribution plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating term frequency distribution plot: {str(e)}")

def plot_term_network(vectorizer: TfidfVectorizer, tfidf_matrix: np.ndarray, 
                      title: str, output_filename: str, n_terms: int = 50) -> None:
    """Plot a network of term co-occurrences."""
    try:
        feature_names = vectorizer.get_feature_names_out()
        term_term_matrix = tfidf_matrix.T @ tfidf_matrix
        
        # Get top n terms
        top_term_indices = term_term_matrix.sum(axis=1).argsort()[0, -n_terms:]
        top_terms = [feature_names[i] for i in top_term_indices.tolist()[0]]
        
        # Create graph
        G = nx.Graph()
        for i, term1 in enumerate(top_terms):
            for j, term2 in enumerate(top_terms[i+1:], start=i+1):
                weight = term_term_matrix[top_term_indices[0, i], top_term_indices[0, j]]
                if weight > 0:
                    G.add_edge(term1, term2, weight=weight)
        
        # Remove isolated nodes
        G.remove_nodes_from(list(nx.isolates(G)))
        
        if len(G.nodes()) == 0:
            logger.warning("No connections found between terms. The graph is empty.")
            return
        
        # Compute communities
        communities = community.greedy_modularity_communities(G)
        
        # Assign colors to communities
        color_map = plt.cm.get_cmap('viridis')
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
        edge_weights = [G[u][v]['weight'] * 10 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.3, edge_color='gray')
        
        plt.title(title, fontsize=24)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, output_filename), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"{title} term network plot saved successfully.")
    except Exception as e:
        logger.error(f"Error creating term network plot: {str(e)}")

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
    preprocessed_docs = [preprocess_text(doc) for doc in documents]
    
    # Perform TF-IDF, PCA, LSA, and t-SNE
    pca_result, lsa_result, tsne_result, vectorizer, pca, lsa, tsne = perform_tfidf_and_dim_reduction(preprocessed_docs)
    
    if pca_result is not None and lsa_result is not None and tsne_result is not None:
        # Generate plots with improved visualizations
        plot_dimension_reduction(pca_result, filenames, labels, "PCA of Document Semantics", "pca_plot.png", "PCA", vectorizer, pca)
        plot_dimension_reduction(lsa_result, filenames, labels, "LSA of Document Semantics", "lsa_plot.png", "LSA", vectorizer, lsa)
        plot_dimension_reduction(tsne_result, filenames, labels, "t-SNE of Document Semantics", "tsne_plot.png", "t-SNE", vectorizer, tsne)
        
        plot_word_importance(vectorizer, pca, "Word Importance (PCA)", "word_importance_pca.png")
        plot_word_importance(vectorizer, lsa, "Word Importance (LSA)", "word_importance_lsa.png")
        
        plot_pca_eigen_terms(vectorizer, pca, "PCA Eigen Terms and Components", "pca_eigen_terms.png")
        
        create_word_cloud(preprocessed_docs, "Word Cloud of All Documents", "word_cloud.png")
        
        plot_prompt_distribution(filenames, "Prompt Distribution and User Prompt Word Frequency", "prompt_distribution.png")
        
        tfidf_matrix = vectorizer.fit_transform(preprocessed_docs)
        plot_topic_modeling(vectorizer, tfidf_matrix, "LDA Topic Modeling", "lda_topics.png", n_topics=5)
        
        plot_heatmap(vectorizer, tfidf_matrix, filenames, "TF-IDF Heatmap of Top Terms", "tfidf_heatmap.png")
        plot_confidence_intervals(vectorizer, tfidf_matrix, filenames, "Confidence Intervals for Top Terms", "confidence_intervals.png")
        plot_system_prompt_comparison(filenames, preprocessed_docs, "System Prompt Comparison", "system_prompt_comparison.png")
        plot_term_frequency_distribution(preprocessed_docs, "Term Frequency Distribution", "term_frequency_distribution.png")
        
        # New visualization
        plot_term_network(vectorizer, tfidf_matrix, "Term Co-occurrence Network", "term_network.png")
    
    logger.info(f"Semantic analysis completed. Plots saved in {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()