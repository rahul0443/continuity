from continuity.retrieval import hybrid
from continuity.retrieval.chunking import Chunk
from continuity.retrieval.hybrid import HybridRetriever

CHUNKS = [
    Chunk("A::0", "A", "e", "SOP", "t", "s", "pump seal replacement procedure"),
    Chunk("B::0", "B", "e", "SOP", "t", "s", "rf match slow tune reflected power fault"),
    Chunk("C::0", "C", "e", "SOP", "t", "s", "chamber pressure drift notes"),
]


def _patch(monkeypatch):
    monkeypatch.setattr(hybrid, "fetch_all_chunks", lambda collection: CHUNKS)
    # Dense ranks A first, so without reranking A leads the fused order.
    monkeypatch.setattr(
        hybrid, "dense_search", lambda collection, query, k=5: [("A::0", 0.9), ("B::0", 0.8), ("C::0", 0.1)]
    )


def test_without_reranker_order_is_unchanged(monkeypatch):
    _patch(monkeypatch)
    out = HybridRetriever(collection=None).retrieve("rf match slow", k=3)
    assert out[0].rerank_score is None


def test_reranker_reorders_and_keeps_fused_score(monkeypatch):
    _patch(monkeypatch)
    scorer = lambda q, ps: [1.0 if "rf match" in p else 0.0 for p in ps]  # noqa: E731
    base = HybridRetriever(collection=None).retrieve("rf match slow", k=3)
    reranked = HybridRetriever(collection=None, reranker=scorer).retrieve("rf match slow", k=3)
    assert reranked[0].chunk.doc_id == "B"
    assert {r.chunk.doc_id: r.fused_score for r in reranked} == {r.chunk.doc_id: r.fused_score for r in base}
