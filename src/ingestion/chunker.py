from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    metadata: dict


def chunk_text(
    text: str,
    metadata: dict,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    separators = ["\n\n", "\n", ". ", " "]
    return _recursive_split(text, metadata, separators, chunk_size, chunk_overlap)


def _recursive_split(
    text: str,
    metadata: dict,
    separators: list[str],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    if len(text) <= chunk_size:
        return [Chunk(text=text.strip(), metadata={**metadata, "chunk_index": 0})] if text.strip() else []

    # Find the best separator that exists in the text
    separator = separators[-1]
    for sep in separators:
        if sep in text:
            separator = sep
            break

    splits = text.split(separator)
    chunks = []
    current = ""

    for split in splits:
        piece = split if not current else separator + split

        if len(current) + len(piece) <= chunk_size:
            current += piece
        else:
            if current.strip():
                chunks.append(current.strip())
            # Start new chunk with overlap from the end of previous
            overlap_text = current[-chunk_overlap:] if chunk_overlap else ""
            current = overlap_text + piece

    if current.strip():
        chunks.append(current.strip())

    return [
        Chunk(text=c, metadata={**metadata, "chunk_index": i})
        for i, c in enumerate(chunks)
    ]
