from src.vectorstore.store import VectorStore


class Retriever:
    def __init__(self, n_results: int = 5):
        self._store = VectorStore()
        self._n_results = n_results

    def retrieve(self, query: str) -> list[dict]:
        results = self._store.query(query, n_results=self._n_results)
        # Filter out low-relevance results (distance > 1.5 means weak match)
        return [r for r in results if r["distance"] < 1.5]