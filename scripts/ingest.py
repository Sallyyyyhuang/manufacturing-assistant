import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.pipeline import ingest_directory


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    print(f"Ingesting documents from: {directory}")
    count = ingest_directory(directory)
    print(f"Done! Ingested {count} chunks.")


if __name__ == "__main__":
    main()
