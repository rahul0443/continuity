"""Optional second-stage reranking of fused retrieval candidates.

First-stage hybrid retrieval (dense + BM25 fused by RRF) is built for recall:
it pulls a wide candidate set cheaply. A cross-encoder reads the query and
each candidate together and scores relevance directly, which is slower but
usually more precise, so it is applied only to the small fused candidate set.

Reranking is OFF by default (RERANKER_MODEL unset), so existing behavior and
the committed baseline metrics are unchanged. Scoring is injected as a plain
callable, which keeps the ordering logic unit-testable without downloading a
model.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Callable, Sequence

from continuity.retrieval.hybrid import RetrievedChunk

# (query, [passage, ...]) -> [score, ...], higher is more relevant.
PairScorer = Callable[[str, Sequence[str]], Sequence[float]]


def rerank(
    query: str,
    candidates: list[RetrievedChunk],
    scorer: PairScorer,
    top_k: int,
) -> list[RetrievedChunk]:
    """Reorders candidates by scorer output and returns the best top_k.

    Ties keep the original fused order (sort is stable). The original
    fused_score is preserved on each result so the score-threshold escalation
    gate keeps its meaning; the reranker score is attached as rerank_score.
    """
    if not candidates:
        return []
    scores = list(scorer(query, [c.chunk.text for c in candidates]))
    if len(scores) != len(candidates):
        raise ValueError(f"scorer returned {len(scores)} scores for {len(candidates)} candidates")
    scored = [replace(c, rerank_score=float(s)) for c, s in zip(candidates, scores)]
    scored.sort(key=lambda c: c.rerank_score, reverse=True)
    return scored[:top_k]


def load_cross_encoder(model_name: str) -> PairScorer:
    """Builds a scorer from a sentence-transformers CrossEncoder.

    Requires the optional extra: pip install "continuity[rerank]".
    """
    try:
        from sentence_transformers import CrossEncoder
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            'Reranking needs sentence-transformers. Install with: pip install "continuity[rerank]"'
        ) from exc
    model = CrossEncoder(model_name)

    def scorer(query: str, passages: Sequence[str]) -> Sequence[float]:
        return model.predict([(query, p) for p in passages]).tolist()

    return scorer
