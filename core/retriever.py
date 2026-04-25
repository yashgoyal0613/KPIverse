"""
Retriever — RAG context retrieval from ChromaDB.
"""
import os
from core.embedder import _get_collection


def retrieve(query: str, n_results: int = 5, source_filter: str = None) -> list[dict]:
    """
    Retrieve top-k relevant chunks for a query.
    Optionally filter by source name.

    Returns list of dicts: [{text, source, chunk, distance}]
    """
    collection = _get_collection()
    total = collection.count()
    if total == 0:
        return []

    n_results = min(n_results, total)

    kwargs = dict(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    if source_filter:
        kwargs["where"] = {"source": source_filter}

    results = collection.query(**kwargs)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text": doc,
            "source": meta.get("source", "unknown"),
            "chunk": meta.get("chunk", 0),
            "distance": round(dist, 4),
            "relevance": round(1 - dist, 4),  # cosine similarity
        }
        for doc, meta, dist in zip(docs, metas, distances)
    ]


def build_context(query: str, n_results: int = 5, source_filter: str = None) -> str:
    """
    Build a formatted context string from retrieved chunks.
    Used as the RAG context block passed to the LLM.
    """
    chunks = retrieve(query, n_results=n_results, source_filter=source_filter)
    if not chunks:
        return "No data has been uploaded yet. Please upload a dataset first."

    lines = ["=== Retrieved Business Data Context ===", ""]
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"[Source: {chunk['source']} | Relevance: {chunk['relevance']:.0%}]")
        lines.append(chunk["text"])
        lines.append("")

    return "\n".join(lines)