import numpy as np
from tabulate import tabulate
from embed import EmbeddingService
from typing import List, Dict, Any
from timeit import default_timer as timer
from datetime import datetime
import orjson
import os


embedding_service = EmbeddingService()


class SearchEngine:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def log_interaction(self, query: str, results: List[tuple], rating: int) -> None:
        """Log query, results and user rating for learning tracking."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'results': results,
            'rating': rating
        }
        os.makedirs('logs', exist_ok=True)
        with open('logs/feedback.log', 'ab') as f:
            f.write(orjson.dumps(log_entry) + b"\n")

    def search(self, query: str, k: int = 5):
        query_embedding = self.embedding_service.embed_query(query)
        top_k = self.embedding_service.get_top_k(query_embedding, k)
        return top_k

    def tabulate_results(self, top_k):
        return tabulate(top_k, headers=["Rank", "Score", "Text"], tablefmt="simple")


def main():
    search_engine = SearchEngine(embedding_service)

    query = input("query: ")
    start_time = timer()

    print(f"searching for \"{query}\"")
    top_k = search_engine.search(query)

    print(search_engine.tabulate_results(top_k))
    print(f"search took {(timer() - start_time) * 1000:.2f} ms")

    try:
        rating = int(input("Rate results from 1 (bad) to 5 (good): "))
    except ValueError:
        rating = 0

    search_engine.log_interaction(query, top_k, rating)


if __name__ == "__main__":
    main()
