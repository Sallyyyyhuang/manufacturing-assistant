import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.pipeline import ingest_directory


def main():
    samples_dir = Path(__file__).resolve().parent.parent / "data" / "samples"

    if not samples_dir.exists():
        print(f"Samples directory not found: {samples_dir}")
        sys.exit(1)

    print(f"Ingesting sample documents from: {samples_dir}")
    count = ingest_directory(samples_dir)
    print(f"Successfully ingested {count} chunks from sample documents.")
    print("You can now start the server and ask questions!")


if __name__ == "__main__":
    main()
