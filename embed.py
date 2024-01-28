import os
import numpy as np
from timeit import default_timer as timer
from typing import List, Dict, Any
import orjson
from fastembed.embedding import DefaultEmbedding
from utils import load_messages
from tqdm import tqdm
from tabulate import tabulate


class EmbeddingService:
    def __init__(self, model: DefaultEmbedding):
        self.model = model

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        embeddings = []
        progress_bar = tqdm(total=len(documents), desc="generating embeddings", unit="doc")

        for document in documents:
            embeddings.extend(self.model.passage_embed([document]))
            progress_bar.update(1)

        progress_bar.close()
        return np.array(embeddings)

    def embed_query(self, query: str) -> np.ndarray:
        return next(self.model.query_embed(query))

    def save_embeddings(self, embeddings: np.ndarray, filename: str):
        np.save(filename, embeddings)

    def load_embeddings(self, filename: str) -> np.ndarray:
        return np.load(filename)


def extract_text(element: Any) -> str:
    if isinstance(element, list):
        return ''.join(map(extract_text, element))
    elif isinstance(element, dict) and "text" in element:
        return extract_text(element["text"])
    elif isinstance(element, str):
        return element
    else:
        return ""


def save_messages_with_embeddings(message_dicts: List[Dict[str, Any]], filename: str):
    try:
        with open(filename, 'w') as json_file:
            json_file.write(orjson.dumps(message_dicts, option=orjson.OPT_INDENT_2).decode('utf-8'))
        print("saved message texts with embeddings!")
    except Exception as e:
        print(f"an error occurred: {e}")


def print_top_k(query_embedding: np.ndarray, embeddings: np.ndarray, documents: List[str], k: int = 5):
    scores = np.dot(embeddings, query_embedding)
    sorted_indices = np.argsort(scores)[::-1]
    unique_documents = list(dict.fromkeys(documents[idx] for idx in sorted_indices if documents[idx]))
    top_k_documents = unique_documents[:k]
    table_data = [(rank+1, f"{scores[documents.index(doc)]:.4f}", doc) for rank, doc in enumerate(top_k_documents)]
    print(tabulate(table_data, headers=["Rank", "Score", "Text"], tablefmt="simple"))


def main():
    embedding_model = DefaultEmbedding()
    embedding_service = EmbeddingService(embedding_model)
    messages = load_messages()
    messages = messages[:1000]
    message_dicts = [{'id': message['id'], 'text': extract_text(message)} for message in messages]
    documents = [message['text'] for message in message_dicts]
    embeddings_filename = 'raw_embeddings.npy'

    if os.path.exists(embeddings_filename):
        start_time = timer()
        embeddings = embedding_service.load_embeddings(embeddings_filename)
        print(f"loaded {len(embeddings)} embeddings in {(timer() - start_time) * 1000:.2f} ms")
    else:
        start_time = timer()
        embeddings = embedding_service.embed_documents(documents)
        embedding_service.save_embeddings(embeddings, embeddings_filename)
        print(f"{len(embeddings)} embeddings generated in {(timer() - start_time) * 1000:.2f} ms")

    for i, message_dict in enumerate(message_dicts):
        message_dict['embedding'] = embeddings[i].tolist()

    save_messages_with_embeddings(message_dicts, 'messages.json')

    query = input("query: ")
    start_time = timer()
    query_embedding = embedding_service.embed_query(query)
    print(f"searching for \"{query}\"")
    print_top_k(query_embedding, embeddings, documents)
    print(f"search took {(timer() - start_time) * 1000:.2f} ms")


if __name__ == "__main__":
    main()
