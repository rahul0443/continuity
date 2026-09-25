"""Eval metrics modeled on FAB-Bench (arXiv:2605.26476), a benchmarking
framework built specifically for RAG systems in semiconductor manufacturing.
FAB-Bench defines six dimensions: retrieval quality, answer relevance,
factual accuracy, completeness, reasoning clarity, and domain specificity.

Retrieval quality is computed deterministically here (precision/recall/MRR
against hand-labeled ground-truth relevant doc_ids per scenario — no LLM
judge, no API key needed). The other five dimensions require semantic
judgment of free-text answers, so they're scored by an LLM judge (Claude)
against a human-authored reference answer, per scenario, 1-5 scale.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from continuity.agent.prompts import JUDGE_SYSTEM_PROMPT, JUDGE_USER_TEMPLATE
from continuity.llm import call_structured
from continuity.retrieval.hybrid import RetrievedChunk

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer_relevance": {"type": "integer", "minimum": 1, "maximum": 5},
        "factual_accuracy": {"type": "integer", "minimum": 1, "maximum": 5},
        "completeness": {"type": "integer", "minimum": 1, "maximum": 5},
        "reasoning_clarity": {"type": "integer", "minimum": 1, "maximum": 5},
        "domain_specificity": {"type": "integer", "minimum": 1, "maximum": 5},
        "justifications": {
            "type": "object",
            "properties": {
                "answer_relevance": {"type": "string"},
                "factual_accuracy": {"type": "string"},
                "completeness": {"type": "string"},
                "reasoning_clarity": {"type": "string"},
                "domain_specificity": {"type": "string"},
            },
        },
    },
    "required": [
        "answer_relevance",
        "factual_accuracy",
        "completeness",
        "reasoning_clarity",
        "domain_specificity",
    ],
}


@dataclass
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    mrr: float
    retrieved_doc_ids: list[str] = field(default_factory=list)


def score_retrieval(retrieved: list[RetrievedChunk], relevant_doc_ids: list[str]) -> RetrievalMetrics:
    retrieved_doc_ids = [r.chunk.doc_id for r in retrieved]
    if not relevant_doc_ids:
        # "Gap" scenarios: nothing should genuinely be relevant. Precision
        # against an empty relevant set is only meaningful as "did it fetch
        # something anyway" — recall/MRR are undefined so we report 1.0
        # trivially (nothing to recall) and let escalation-accuracy (in the
        # harness) carry the real signal for these scenarios.
        return RetrievalMetrics(precision_at_k=0.0, recall_at_k=1.0, mrr=0.0, retrieved_doc_ids=retrieved_doc_ids)

    relevant_set = set(relevant_doc_ids)
    hits = [1 if doc_id in relevant_set else 0 for doc_id in retrieved_doc_ids]
    precision = sum(hits) / len(hits) if hits else 0.0
    unique_relevant_hit = len({d for d in retrieved_doc_ids if d in relevant_set})
    recall = unique_relevant_hit / len(relevant_set)
    mrr = 0.0
    for rank, hit in enumerate(hits, start=1):
        if hit:
            mrr = 1.0 / rank
            break
    return RetrievalMetrics(precision_at_k=precision, recall_at_k=recall, mrr=mrr, retrieved_doc_ids=retrieved_doc_ids)


def judge_answer(query: str, generated_answer: str, reference_answer: str, context: str) -> dict:
    return call_structured(
        system=JUDGE_SYSTEM_PROMPT,
        user=JUDGE_USER_TEMPLATE.format(
            query=query, generated_answer=generated_answer, reference_answer=reference_answer, context=context
        ),
        tool_name="submit_scores",
        tool_description="Submit the FAB-Bench-style evaluation scores.",
        input_schema=JUDGE_SCHEMA,
        max_tokens=1024,
    )
