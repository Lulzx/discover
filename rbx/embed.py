"""Utilities for generating and querying text embeddings."""

import os
from pathlib import Path
from timeit import default_timer as timer

import numpy as np
from fastembed.embedding import DefaultEmbedding
from tqdm import tqdm

from .utils import get_messages, time_elapsed


class EmbeddingService:
    """Generate and query vector embeddings for stored messages."""

    def __init__(self, cache_file: str = "cache/embeddings.npy") -> None:
        self.model = self.load_model()
        self.cache_file = cache_file
        self.documents = get_messages()
        self.embeddings = self.get_embeddings()

    def load_model(self) -> DefaultEmbedding:
        """Load the default embedding model and report initialization time."""
        start_time = timer()
        model = DefaultEmbedding()
        print(f"Model loaded in {time_elapsed(start_time)} ms")
        return model

    def embed_documents(self) -> np.ndarray:
        """Generate embeddings for all stored documents."""
        embeddings = []
        progress_bar = tqdm(total=len(self.documents), desc="generating embeddings", unit="doc")
        for document in self.documents:
            embeddings.extend(self.model.passage_embed([document]))
            progress_bar.update(1)
        progress_bar.close()
        return np.array(embeddings)

    def embed_query(self, query: str) -> np.ndarray:
        """Return the embedding vector for a query string."""
        return next(self.model.query_embed(query))

    def get_embeddings(self) -> np.ndarray:
        """Load cached embeddings or generate and cache them."""
        if os.path.exists(self.cache_file):
            start_time = timer()
            embeddings = np.load(self.cache_file)
            print(f"embeddings loaded in {time_elapsed(start_time)} ms")
        else:
            embeddings = self.embed_documents()
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            np.save(self.cache_file, embeddings)
            print("saved generated embeddings!")
        return embeddings

    def get_top_k(self, query_embedding: np.ndarray, k: int = 5):
        """Return top-*k* documents ranked by cosine similarity."""
        scores = np.dot(self.embeddings, query_embedding)
        sorted_indices = np.argsort(scores)[::-1]
        unique_documents = list(
            dict.fromkeys(self.documents[idx] for idx in sorted_indices if self.documents[idx])
        )
        top_k_documents = unique_documents[:k]
        table_data = [
            (rank + 1, f"{scores[self.documents.index(doc)]:.4f}", f"{doc[:50]}..")
            for rank, doc in enumerate(top_k_documents)
        ]
        return table_data
