from continuity.retrieval.chunking import Chunk
from continuity.retrieval.hybrid import RetrievedChunk
from continuity.eval.metrics import score_retrieval


def _fake_retrieved(doc_ids: list[str]) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk=Chunk(
                chunk_id=f"{d}::0",
                doc_id=d,
                equipment="test",
                doc_type="SOP",
                title="t",
                section="s",
                text="text",
            ),
            fused_score=1.0 / (i + 1),
            dense_rank=i,
            bm25_rank=i,
        )
        for i, d in enumerate(doc_ids)
    ]


def test_perfect_retrieval_scores_1():
    retrieved = _fake_retrieved(["A", "B"])
    m = score_retrieval(retrieved, ["A", "B"])
    assert m.precision_at_k == 1.0
    assert m.recall_at_k == 1.0
    assert m.mrr == 1.0


def test_no_hits_scores_0():
    retrieved = _fake_retrieved(["X", "Y"])
    m = score_retrieval(retrieved, ["A"])
    assert m.precision_at_k == 0.0
    assert m.recall_at_k == 0.0
    assert m.mrr == 0.0


def test_partial_hit_ranked_second():
    retrieved = _fake_retrieved(["X", "A"])
    m = score_retrieval(retrieved, ["A"])
    assert m.precision_at_k == 0.5
    assert m.recall_at_k == 1.0
    assert m.mrr == 0.5  # hit at rank 2


def test_empty_relevant_set_gap_scenario():
    retrieved = _fake_retrieved(["X", "Y"])
    m = score_retrieval(retrieved, [])
    assert m.recall_at_k == 1.0  # nothing to recall, trivially satisfied
