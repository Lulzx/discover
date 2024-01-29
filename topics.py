import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import hdbscan
from scipy.stats import gaussian_kde
from tqdm import tqdm

# Define a folder to save and retrieve calculated data
data_folder = 'calculated_cache'
os.makedirs(data_folder, exist_ok=True)

# Function to save or load data
def save_or_load(filename, calculation_function=None, *args, **kwargs):
    filepath = os.path.join(data_folder, filename)
    if os.path.exists(filepath):
        print(f"Loading {filename} from file...")
        data = np.load(filepath)
    else:
        if calculation_function is None:
            raise ValueError("calculation_function must be provided if file does not exist.")
        print(f"Calculating {filename}...")
        data = calculation_function(*args, **kwargs)
        np.save(filepath, data)
    return data

# Step 1: Load embeddings
embeddings = save_or_load('embeddings.npy')

# Step 2: Dimensionality reduction with PCA
def perform_pca(data):
    pca = PCA(n_components=50)
    return pca.fit_transform(data)

embeddings_pca = save_or_load('embeddings_pca.npy', perform_pca, embeddings)

# Step 3: Further reduction with t-SNE
def perform_tsne(data):
    tsne = TSNE(n_components=2, random_state=42, verbose=1)
    return tsne.fit_transform(data)

embeddings_reduced = save_or_load('embeddings_tsne.npy', perform_tsne, embeddings_pca)

# Step 4: Clustering with HDBSCAN
def perform_hdbscan(data):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
    return clusterer.fit_predict(data)

cluster_labels = save_or_load('cluster_labels.npy', perform_hdbscan, embeddings_reduced)

# Step 5: Visualization with Seaborn including cluster boundaries
plt.figure(figsize=(10, 8))

# Create a color palette with a distinct color for each cluster
palette = sns.color_palette('bright', np.unique(cluster_labels).max() + 1)

# Plot each cluster
for i, color in tqdm(enumerate(palette), desc='Plotting clusters', total=len(palette)):
    # Extract the points that belong to the current cluster
    points = embeddings_reduced[cluster_labels == i]

    # Skip if there are no points in this cluster
    if len(points) == 0:
        continue

    # Plot the points
    sns.scatterplot(x=points[:, 0], y=points[:, 1], color=color, label=f'Cluster {i}')

    # Calculate the density of the points using Gaussian KDE
    try:
        kde = gaussian_kde(points.T)
        # Create a grid of points for evaluation
        x_min, x_max = points[:, 0].min() - 1, points[:, 0].max() + 1
        y_min, y_max = points[:, 1].min() - 1, points[:, 1].max() + 1
        x, y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
        # Evaluate the density on the grid
        z = kde(np.vstack([x.ravel(), y.ravel()]))
        # Reshape for the contour plot
        z = z.reshape(x.shape)
        # Plot the density contour
        plt.contour(x, y, z, colors=[color], linewidths=2)
    except np.linalg.LinAlgError:
        pass
        # print(f"Could not plot Gaussian KDE for cluster {i} due to singularity.")

# Unassigned points (noise) are plotted in gray
noise_points = embeddings_reduced[cluster_labels == -1]
if len(noise_points) > 0:
    sns.scatterplot(x=noise_points[:, 0], y=noise_points[:, 1], color=(0.5, 0.5, 0.5), label='Noise')

plt.title('HDBSCAN clustering with t-SNE reduced embeddings')
plt.xlabel('t-SNE dimension 1')
plt.ylabel('t-SNE dimension 2')
plt.legend()
plt.show()
