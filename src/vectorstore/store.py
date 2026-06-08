import chromadb
from chromadb.utils import embedding_functions

from src.config import settings


class VectorStore:
    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        self._collection = self._client.get_or_create_collection(
            name="manufacturing_docs",
            embedding_function=self._embedding_fn,
        )

    def add_chunks(self, chunks) -> None:
        self._collection.add(
            ids=[f"{c.metadata['source']}_{c.metadata['chunk_index']}" for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )

    def query(self, text: str, n_results: int = 5) -> list[dict]:
        results = self._collection.query(
            query_texts=[text],
            n_results=n_results,
        )
        output = []
        for i in range(len(results["documents"][0])):
            output.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

    def list_documents(self) -> list[str]:
        all_metadata = self._collection.get()["metadatas"]
        sources = set(m["source"] for m in all_metadata if "source" in m)
        return sorted(sources)

    def delete_collection(self) -> None:
        self._client.delete_collection("manufacturing_docs")

    @property
    def count(self) -> int:
        return self._collection.count()
