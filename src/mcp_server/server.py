from mcp.server.fastmcp import FastMCP

from src.rag.generator import Generator
from src.vectorstore.store import VectorStore

mcp = FastMCP("Manufacturing Knowledge Assistant")
generator = Generator()


@mcp.tool()
def query_knowledge_base(question: str) -> str:
    """Ask a question about manufacturing documents in the knowledge base.

    Use this tool when the user asks about manufacturing processes,
    quality control, SPC, OEE, FMEA, or other manufacturing topics
    that may be covered in the ingested documents.

    Args:
        question: The manufacturing-related question to answer
    """
    return generator.ask(question)


@mcp.tool()
def list_available_documents() -> str:
    """List all documents currently in the manufacturing knowledge base.

    Use this to see what information is available before querying.
    """
    store = VectorStore()
    docs = store.list_documents()
    if not docs:
        return "No documents in the knowledge base. Documents need to be ingested first."
    return f"Available documents ({len(docs)}):\n" + "\n".join(f"- {d}" for d in docs)


@mcp.tool()
def search_documents(query: str, n_results: int = 5) -> str:
    """Search for specific text passages in the manufacturing knowledge base.

    Returns raw matching chunks without AI interpretation.
    Useful for finding exact specifications, values, or procedures.

    Args:
        query: What to search for
        n_results: How many results to return (default 5)
    """
    store = VectorStore()
    results = store.query(query, n_results=n_results)
    if not results:
        return "No matching passages found."

    output = []
    for i, r in enumerate(results, 1):
        source = r["metadata"].get("source", "unknown")
        output.append(f"[{i}] From: {source}\n{r['text'][:300]}")
    return "\n\n---\n\n".join(output)


if __name__ == "__main__":
    mcp.run()
