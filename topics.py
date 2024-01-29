import os
import numpy as np
import seaborn as sns
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import hdbscan
from scipy.stats import gaussian_kde
from tqdm import tqdm
import orjson

from utils import get_messages

cache_folder = 'cache'
os.makedirs(cache_folder, exist_ok=True)

def save_or_load(filename, calculation_function=None, *args, **kwargs):
    filepath = os.path.join(cache_folder, filename)
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
    clusterer = hdbscan.HDBSCAN(min_cluster_size=30, gen_min_span_tree=True)
    return clusterer.fit_predict(data)

cluster_labels = save_or_load('cluster_labels.npy', perform_hdbscan, embeddings_reduced)

unique_labels = np.unique(cluster_labels)
num_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
print(f"Number of clusters: {num_clusters}")

def find_best_min_cluster_size(data, min_size_start, min_size_end, step=1):
    best_min_cluster_size = None
    best_silhouette_score = -1

    for min_cluster_size in range(min_size_start, min_size_end + 1, step):
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, gen_min_span_tree=True)
        cluster_labels = clusterer.fit_predict(data)

        filtered_labels = cluster_labels[cluster_labels != -1]
        filtered_data = data[cluster_labels != -1]

        if len(np.unique(filtered_labels)) > 1:
            score = silhouette_score(filtered_data, filtered_labels)
            print(f"min_cluster_size: {min_cluster_size}, silhouette_score: {score}")

            if score > best_silhouette_score:
                best_silhouette_score = score
                best_min_cluster_size = min_cluster_size

    return best_min_cluster_size, best_silhouette_score

# best_size, best_score = find_best_min_cluster_size(embeddings_reduced, 5, 50, step=5)
# print(f"The best min_cluster_size is {best_size} with a silhouette score of {best_score}")
# The best min_cluster_size is 30 with a silhouette score of 0.6569266

messages = get_messages()

cluster_texts_folder = os.path.join(cache_folder, 'cluster_texts')
os.makedirs(cluster_texts_folder, exist_ok=True)

for cluster_label in np.unique(cluster_labels):
    if cluster_label == -1:
        continue

    indices_in_cluster = np.where(cluster_labels == cluster_label)[0]

    cluster_messages = []

    for index in indices_in_cluster:
        message = messages[int(index)]
        cluster_messages.append({'id': int(index), 'text': message})

    cluster_file_path = os.path.join('cache', 'cluster_texts', f'cluster_{cluster_label}.json')
    with open(cluster_file_path, 'wb') as cluster_file:
        cluster_file.write(orjson.dumps(cluster_messages))

    print(f"Stored messages for Cluster {cluster_label} in {cluster_file_path}")


plt.figure(figsize=(10, 8))

palette = sns.color_palette('bright', np.unique(cluster_labels).max() + 1)

for i, color in tqdm(enumerate(palette), desc='Plotting clusters', total=len(palette)):
    points = embeddings_reduced[cluster_labels == i]

    if len(points) == 0:
        continue

    sns.scatterplot(x=points[:, 0], y=points[:, 1], color=color)

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
    sns.scatterplot(x=noise_points[:, 0], y=noise_points[:, 1], color=(0.5, 0.5, 0.5))

plt.title('HDBSCAN clustering with t-SNE reduced embeddings')
plt.xlabel('t-SNE dimension 1')
plt.ylabel('t-SNE dimension 2')
plt.legend()
plt.show()
