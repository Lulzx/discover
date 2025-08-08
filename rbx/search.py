"""Simple search engine wrapper around the embedding service."""

import os
from datetime import datetime
from timeit import default_timer as timer
from typing import List

import orjson
from tabulate import tabulate

from .embed import EmbeddingService

embedding_service = EmbeddingService()


class SearchEngine:
    """Provide search over message embeddings and log feedback."""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service

    def log_interaction(self, query: str, results: List[tuple], rating: int) -> None:
        """Persist the query, results and a user rating for later analysis."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "results": results,
            "rating": rating,
        }
        os.makedirs("logs", exist_ok=True)
        with open("logs/feedback.log", "ab") as f:
            f.write(orjson.dumps(log_entry) + b"\n")

    def search(self, query: str, k: int = 5):
        """Return the top *k* results for *query*."""
        query_embedding = self.embedding_service.embed_query(query)
        return self.embedding_service.get_top_k(query_embedding, k)

    def tabulate_results(self, top_k):
        """Format search results as a table for CLI display."""
        return tabulate(top_k, headers=["Rank", "Score", "Text"], tablefmt="simple")


def main() -> None:  # pragma: no cover - convenience script
    search_engine = SearchEngine(embedding_service)

    query = input("query: ")
    start_time = timer()

    print(f'searching for "{query}"')
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
