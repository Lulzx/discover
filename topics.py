import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import hdbscan
from scipy.stats import gaussian_kde
from tqdm import tqdm

data_folder = 'cache'
os.makedirs(data_folder, exist_ok=True)

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

embeddings = save_or_load('embeddings.npy')

def perform_pca(data):
    pca = PCA(n_components=50)
    return pca.fit_transform(data)

embeddings_pca = save_or_load('embeddings_pca.npy', perform_pca, embeddings)

def perform_tsne(data):
    tsne = TSNE(n_components=2, random_state=42, verbose=1)
    return tsne.fit_transform(data)

embeddings_reduced = save_or_load('embeddings_tsne.npy', perform_tsne, embeddings_pca)

def perform_hdbscan(data):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
    return clusterer.fit_predict(data)

cluster_labels = save_or_load('cluster_labels.npy', perform_hdbscan, embeddings_reduced)

plt.figure(figsize=(10, 8))

palette = sns.color_palette('bright', np.unique(cluster_labels).max() + 1)

for i, color in tqdm(enumerate(palette), desc='Plotting clusters', total=len(palette)):
    points = embeddings_reduced[cluster_labels == i]

    if len(points) == 0:
        continue

    sns.scatterplot(x=points[:, 0], y=points[:, 1], color=color, label=f'Cluster {i}')

    try:
        kde = gaussian_kde(points.T)
        x_min, x_max = points[:, 0].min() - 1, points[:, 0].max() + 1
        y_min, y_max = points[:, 1].min() - 1, points[:, 1].max() + 1
        x, y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
        z = kde(np.vstack([x.ravel(), y.ravel()]))
        z = z.reshape(x.shape)
        plt.contour(x, y, z, colors=[color], linewidths=2)
    except np.linalg.LinAlgError:
        pass
        # print(f"Could not plot Gaussian KDE for cluster {i} due to singularity.")

noise_points = embeddings_reduced[cluster_labels == -1]
if len(noise_points) > 0:
    sns.scatterplot(x=noise_points[:, 0], y=noise_points[:, 1], color=(0.5, 0.5, 0.5), label='Noise')

plt.title('HDBSCAN clustering with t-SNE reduced embeddings')
plt.xlabel('t-SNE dimension 1')
plt.ylabel('t-SNE dimension 2')
plt.legend()
plt.show()
