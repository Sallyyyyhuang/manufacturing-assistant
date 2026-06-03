import anthropic

from src.config import settings
from src.rag.retriever import Retriever

SYSTEM_PROMPT = """You are a manufacturing knowledge assistant. Answer questions based on the provided context from manufacturing documents.

Rules:
- Only answer based on the provided context
- If the context doesn't contain enough information, say so
- Cite which source document the information comes from
- Be concise and technical"""


class Generator:
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._retriever = Retriever()

    def ask(self, question: str) -> str:
        # Step 1: Retrieve relevant chunks
        chunks = self._retriever.retrieve(question)

        if not chunks:
            return "I couldn't find relevant information in the knowledge base for that question."

        # Step 2: Build context from retrieved chunks
        context = self._format_context(chunks)

        # Step 3: Call Claude with the context
        message = self._client.messages.create(
            model=settings.model_name,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                }
            ],
        )
        return message.content[0].text

    def ask_stream(self, question: str):
        """Generator that yields tokens as they arrive."""
        chunks = self._retriever.retrieve(question)

        if not chunks:
            yield "I couldn't find relevant information in the knowledge base for that question."
            return

        context = self._format_context(chunks)

        with self._client.messages.stream(
            model=settings.model_name,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                }
            ],
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _format_context(self, chunks: list[dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"].get("source", "unknown")
            page = chunk["metadata"].get("page", "")
            page_str = f" (page {page})" if page else ""
            parts.append(f"[{i}] From: {source}{page_str}\n{chunk['text']}")
        return "\n\n---\n\n".join(parts)
