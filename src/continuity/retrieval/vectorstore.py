"""Thin wrapper around a persistent Chroma collection.

Uses chromadb's bundled default embedding function (a small local ONNX
MiniLM model) rather than a paid embeddings API, so indexing and dense
retrieval work with zero API keys and zero per-call cost. Generation and
judging (in continuity.agent / continuity.eval) are the parts that need an
Anthropic API key — retrieval does not.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.utils import embedding_functions

from continuity.retrieval.chunking import Chunk

COLLECTION_NAME = "continuity"


def get_client(persist_dir: Path) -> chromadb.ClientAPI:
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(persist_dir), settings=chromadb.Settings(anonymized_telemetry=False)
    )


def get_collection(client: chromadb.ClientAPI):
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)


def index_chunks(collection, chunks: Iterable[Chunk]) -> int:
    chunks = list(chunks)
    if not chunks:
        return 0
    collection.upsert(
        ids=[c.chunk_id for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "doc_id": c.doc_id,
                "equipment": c.equipment,
                "doc_type": c.doc_type,
                "title": c.title,
                "section": c.section,
            }
            for c in chunks
        ],
    )
    return len(chunks)


def fetch_all_chunks(collection) -> list[Chunk]:
    """Reloads every indexed chunk from Chroma, used to rebuild the in-memory
    BM25 index without keeping a second copy of the corpus on disk."""
    raw = collection.get(include=["documents", "metadatas"])
    chunks = []
    for chunk_id, text, meta in zip(raw["ids"], raw["documents"], raw["metadatas"]):
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                doc_id=meta["doc_id"],
                equipment=meta["equipment"],
                doc_type=meta["doc_type"],
                title=meta["title"],
                section=meta["section"],
                text=text,
            )
        )
    return chunks


def dense_search(collection, query: str, k: int = 5) -> list[tuple[str, float]]:
    """Returns [(chunk_id, similarity_score)] ranked best-first.

    Chroma's default distance is squared L2 on normalized embeddings; we
    convert to a similarity score (higher = better) so it composes cleanly
    with BM25 scores inside reciprocal rank fusion.
    """
    res = collection.query(query_texts=[query], n_results=k, include=["distances"])
    ids = res["ids"][0]
    distances = res["distances"][0]
    return [(chunk_id, 1.0 / (1.0 + dist)) for chunk_id, dist in zip(ids, distances)]
