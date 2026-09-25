"""Hybrid dense + lexical retrieval with Reciprocal Rank Fusion (RRF).

Fault descriptions from shift engineers frequently contain exact tokens that
matter a lot and embed poorly — part numbers, error codes, tool IDs like
"AMX-5200". Pure dense retrieval under-weights exact lexical matches on this
kind of text; pure BM25 misses paraphrases and symptom descriptions that
don't share vocabulary with the source docs. Fusing both rankings is the
standard fix, and it's what production maintenance-copilot systems in this
space actually do (see README competitive landscape section) rather than
relying on a single retriever.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from continuity.retrieval.chunking import Chunk
from continuity.retrieval.vectorstore import dense_search, fetch_all_chunks

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class RetrievedChunk:
    chunk: Chunk
    fused_score: float
    dense_rank: int | None
    bm25_rank: int | None


class HybridRetriever:
    """Rebuilds an in-memory BM25 index from the Chroma collection's stored
    documents on construction. Fine at this corpus size (tens to low
    hundreds of chunks); a larger deployment would persist the BM25 index
    separately instead of reloading it from Chroma each time."""

    def __init__(self, collection, rrf_k: int = 60):
        self.collection = collection
        self.rrf_k = rrf_k
        self.chunks = fetch_all_chunks(collection)
        self.chunks_by_id = {c.chunk_id: c for c in self.chunks}
        self._bm25 = BM25Okapi([_tokenize(c.text) for c in self.chunks]) if self.chunks else None

    def _bm25_search(self, query: str, k: int) -> list[tuple[str, float]]:
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        ranked_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(self.chunks[i].chunk_id, float(scores[i])) for i in ranked_idx]

    def retrieve(self, query: str, k: int = 5, fetch_k: int = 15) -> list[RetrievedChunk]:
        if not self.chunks:
            return []
        dense_results = dense_search(self.collection, query, k=min(fetch_k, len(self.chunks)))
        bm25_results = self._bm25_search(query, k=min(fetch_k, len(self.chunks)))

        dense_rank = {chunk_id: r for r, (chunk_id, _) in enumerate(dense_results)}
        bm25_rank = {chunk_id: r for r, (chunk_id, _) in enumerate(bm25_results)}

        all_ids = set(dense_rank) | set(bm25_rank)
        fused: list[RetrievedChunk] = []
        for chunk_id in all_ids:
            score = 0.0
            if chunk_id in dense_rank:
                score += 1.0 / (self.rrf_k + dense_rank[chunk_id] + 1)
            if chunk_id in bm25_rank:
                score += 1.0 / (self.rrf_k + bm25_rank[chunk_id] + 1)
            fused.append(
                RetrievedChunk(
                    chunk=self.chunks_by_id[chunk_id],
                    fused_score=score,
                    dense_rank=dense_rank.get(chunk_id),
                    bm25_rank=bm25_rank.get(chunk_id),
                )
            )
        fused.sort(key=lambda r: r.fused_score, reverse=True)
        return fused[:k]
