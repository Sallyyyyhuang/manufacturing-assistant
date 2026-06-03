from pathlib import Path

from src.config import settings
from src.ingestion.loader import load_document
from src.ingestion.chunker import chunk_text, Chunk
from src.vectorstore.store import VectorStore


def ingest_directory(directory: str | Path) -> int:
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    store = VectorStore()
    all_chunks: list[Chunk] = []

    for file_path in directory.iterdir():
        if file_path.suffix.lower() in (".pdf", ".docx", ".txt", ".csv", "xlsx", "xls"):
            documents = load_document(file_path)
            for doc in documents:
                chunks = chunk_text(
                    doc.text,
                    doc.metadata,
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                )
                all_chunks.extend(chunks)

    if all_chunks:
        store.add_chunks(all_chunks)

    return len(all_chunks)
