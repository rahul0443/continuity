import pytest

from continuity.retrieval.chunking import Chunk
from continuity.retrieval.hybrid import RetrievedChunk
from continuity.retrieval.rerank import rerank


def _rc(doc_id, text, fused):
    return RetrievedChunk(
        chunk=Chunk(chunk_id=f"{doc_id}::0", doc_id=doc_id, equipment="e", doc_type="SOP",
                    title="t", section="s", text=text),
        fused_score=fused, dense_rank=0, bm25_rank=0,
    )


def _keyword_scorer(query, passages):
    return [1.0 if "RF match" in p else 0.0 for p in passages]


def test_rerank_promotes_the_better_passage():
    cands = [_rc("A", "unrelated pump note", 0.03), _rc("B", "RF match tuning fault", 0.02)]
    out = rerank("rf match slow", cands, _keyword_scorer, top_k=2)
    assert [r.chunk.doc_id for r in out] == ["B", "A"]


def test_rerank_truncates_to_top_k_and_keeps_fused_score():
    cands = [_rc("A", "x", 0.03), _rc("B", "RF match", 0.02), _rc("C", "y", 0.01)]
    out = rerank("q", cands, _keyword_scorer, top_k=1)
    assert len(out) == 1
    assert out[0].chunk.doc_id == "B"
    assert out[0].fused_score == 0.02
    assert out[0].rerank_score == 1.0


def test_rerank_ties_keep_fused_order():
    cands = [_rc("A", "x", 0.03), _rc("B", "y", 0.02)]
    out = rerank("q", cands, lambda q, ps: [0.5] * len(ps), top_k=2)
    assert [r.chunk.doc_id for r in out] == ["A", "B"]


def test_rerank_empty_returns_empty():
    assert rerank("q", [], _keyword_scorer, top_k=3) == []


def test_scorer_length_mismatch_raises():
    with pytest.raises(ValueError):
        rerank("q", [_rc("A", "x", 0.1)], lambda q, ps: [1.0, 2.0], top_k=1)
