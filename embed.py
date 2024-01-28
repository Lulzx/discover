import os
import orjson
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Any
from timeit import default_timer as timer
from utils import load_messages, time_elapsed
from fastembed.embedding import DefaultEmbedding


class EmbeddingService:
    def __init__(self):
        self.model = self.load_model()
        self.filename = "embeddings.npy"
        self.documents = self.get_documents()
        self.embeddings = self.get_embeddings()


    def load_model(self) -> DefaultEmbedding:
        start_time = timer()
        model = DefaultEmbedding()
        print(f"Model loaded in {time_elapsed(start_time)} ms")
        return model


    def embed_documents(self) -> np.ndarray:
        embeddings = []
        progress_bar = tqdm(total=len(self.documents), desc="generating embeddings", unit="doc")
        for document in self.documents:
            embeddings.extend(self.model.passage_embed([document]))
            progress_bar.update(1)
        progress_bar.close()
        return np.array(embeddings)


    def get_documents(self) -> List[str]:
        return [self.extract_text(message) for message in self.get_messages()]


    def get_messages(self) -> List[Dict[str, Any]]:
        messages = load_messages()
        return [{'id': message['id'], 'text': self.extract_text(message)} for message in messages]


    def embed_query(self, query: str) -> np.ndarray:
        return next(self.model.query_embed(query))


    def extract_text(self, element: Any) -> str:
        if isinstance(element, list):
            return ''.join(map(self.extract_text, element))
        elif isinstance(element, dict) and "text" in element:
            return self.extract_text(element["text"])
        elif isinstance(element, str):
            return element
        else:
            return ""


    def get_embeddings(self) -> np.ndarray:
        if os.path.exists(self.filename):
            start_time = timer()
            embeddings = np.load(self.filename)
            print(f"embeddings loaded in {time_elapsed(start_time)} ms")
        else:
            embeddings = self.embed_documents()
            np.save(self.filename, embeddings)
            print("saved generated embeddings!")
        return embeddings


    def get_top_k(self, query_embedding: np.ndarray, k: int = 5):
        scores = np.dot(self.embeddings, query_embedding)
        sorted_indices = np.argsort(scores)[::-1]
        unique_documents = list(dict.fromkeys(self.documents[idx] for idx in sorted_indices if self.documents[idx]))
        top_k_documents = unique_documents[:k]
        table_data = [(rank+1, f"{scores[self.documents.index(doc)]:.4f}", f"{doc[:50]}..") for rank, doc in enumerate(top_k_documents)]
        return table_data
