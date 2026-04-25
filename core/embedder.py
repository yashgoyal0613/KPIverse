"""
Embedder — chunks text and stores/retrieves from ChromaDB.
Uses sentence-transformers for local embeddings (no API cost).
"""
import os
import hashlib
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
COLLECTION_NAME = "kpi_insights"

# Sentence-transformers local embedding (no API key needed)
_EMBED_MODEL = "all-MiniLM-L6-v2"


def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_EMBED_MODEL
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _doc_id(source: str, chunk_index: int) -> str:
    h = hashlib.md5(source.encode()).hexdigest()[:8]
    return f"{h}_chunk_{chunk_index}"


def embed_text(text: str, source_name: str, metadata: dict = None) -> int:
    """
    Embed a text document into ChromaDB.
    Returns the number of chunks stored.
    """
    collection = _get_collection()
    chunks = _chunk_text(text)
    if not chunks:
        return 0

    ids = [_doc_id(source_name, i) for i in range(len(chunks))]
    meta_list = [{**(metadata or {}), "source": source_name, "chunk": i} for i in range(len(chunks))]

    # Upsert to avoid duplicates on re-upload
    collection.upsert(documents=chunks, ids=ids, metadatas=meta_list)
    return len(chunks)


def list_sources() -> list[str]:
    """Return unique source names stored in ChromaDB."""
    collection = _get_collection()
    results = collection.get(include=["metadatas"])
    sources = list({m.get("source", "unknown") for m in results["metadatas"]})
    return sorted(sources)


def delete_source(source_name: str) -> int:
    """Delete all chunks for a given source. Returns count deleted."""
    collection = _get_collection()
    results = collection.get(where={"source": source_name}, include=["metadatas"])
    ids = results["ids"]
    if ids:
        collection.delete(ids=ids)
    return len(ids)


def collection_stats() -> dict:
    collection = _get_collection()
    count = collection.count()
    sources = list_sources()
    return {"total_chunks": count, "sources": sources, "source_count": len(sources)}