import numpy as np
from typing import List, Tuple
from embed import EmbeddingService


def find_related_documents(k: int = 5) -> List[Tuple[int, int, float]]:
    """Return top k pairs of documents with highest cosine similarity."""
    service = EmbeddingService()
    embeddings = service.embeddings
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / (norm + 1e-8)
    similarity_matrix = np.dot(normalized, normalized.T)

    np.fill_diagonal(similarity_matrix, -1)
    pairs = []
    for _ in range(k):
        idx = np.unravel_index(similarity_matrix.argmax(), similarity_matrix.shape)
        score = similarity_matrix[idx]
        pairs.append((int(idx[0]), int(idx[1]), float(score)))
        similarity_matrix[idx] = -1
        similarity_matrix[idx[1], idx[0]] = -1
    return pairs


if __name__ == '__main__':
    for a, b, score in find_related_documents():
        print(f"doc {a} <-> doc {b} = {score:.4f}")
