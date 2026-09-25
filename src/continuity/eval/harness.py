"""Eval harness: runs every scenario in data/eval/fault_scenarios.json
through the full agent graph (or, in --dry-run mode, through retrieval
only) and reports FAB-Bench-style metrics.

--dry-run needs no ANTHROPIC_API_KEY: it validates the hybrid retriever
alone against the hand-labeled ground truth (precision@k, recall@k, MRR,
plus whether the cheap score-threshold gate would have escalated). The full
run additionally exercises the LangGraph agent's triage/answer/escalate
routing and LLM-judges each generated answer against the reference answer.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from continuity.agent.graph import run_continuity_agent
from continuity.config import settings
from continuity.eval.metrics import judge_answer, score_retrieval
from continuity.retrieval.hybrid import HybridRetriever
from continuity.retrieval.vectorstore import get_client, get_collection


def _load_scenarios() -> list[dict]:
    path = settings.eval_dir / "fault_scenarios.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _format_answer_text(result: dict) -> str:
    if result.get("escalated"):
        return result["escalation"]["message"]
    answer = result.get("answer", {})
    lines = [answer.get("summary", "")]
    for cause in answer.get("causes", []):
        lines.append(
            f"- {cause['cause']} (confidence: {cause['confidence']}, "
            f"sources: {', '.join(cause.get('cited_sources', []))}) -> {cause['recommended_action']}"
        )
    return "\n".join(lines)


def _format_context(retrieved) -> str:
    return "\n\n".join(f"[{r.chunk.doc_id}] {r.chunk.text}" for r in retrieved)


def run_eval(dry_run: bool = False, out_path: str = "eval_results.json") -> dict[str, Any]:
    scenarios = _load_scenarios()
    client = get_client(settings.chroma_persist_dir)
    collection = get_collection(client)
    retriever = HybridRetriever(collection)

    per_scenario: list[dict[str, Any]] = []

    for scenario in scenarios:
        retrieved = retriever.retrieve(scenario["query"], k=settings.retrieval_top_k)
        retrieval_metrics = score_retrieval(retrieved, scenario["relevant_doc_ids"])
        top_score = retrieved[0].fused_score if retrieved else 0.0
        would_gate_escalate = top_score < settings.min_fused_score_threshold

        record: dict[str, Any] = {
            "id": scenario["id"],
            "equipment": scenario["equipment"],
            "expects_escalation": scenario["expects_escalation"],
            "retrieval": {
                "precision_at_k": retrieval_metrics.precision_at_k,
                "recall_at_k": retrieval_metrics.recall_at_k,
                "mrr": retrieval_metrics.mrr,
                "retrieved_doc_ids": retrieval_metrics.retrieved_doc_ids,
            },
            "score_gate_would_escalate": would_gate_escalate,
        }

        if not dry_run:
            result = run_continuity_agent(scenario["query"], scenario.get("equipment"))
            escalated = bool(result.get("escalated"))
            record["escalated"] = escalated
            record["escalation_correct"] = escalated == scenario["expects_escalation"]
            generated_answer_text = _format_answer_text(result)
            record["generated_answer"] = generated_answer_text

            if not scenario["expects_escalation"]:
                judged = judge_answer(
                    query=scenario["query"],
                    generated_answer=generated_answer_text,
                    reference_answer=scenario["reference_answer"],
                    context=_format_context(retrieved),
                )
                record["judge_scores"] = judged

        per_scenario.append(record)

    report = _aggregate(per_scenario, dry_run=dry_run)
    report["scenarios"] = per_scenario

    Path(out_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    _print_report(report, dry_run=dry_run)
    return report


def _aggregate(records: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    agg: dict[str, Any] = {
        "n_scenarios": len(records),
        "dry_run": dry_run,
        "retrieval": {
            "mean_precision_at_k": statistics.mean(r["retrieval"]["precision_at_k"] for r in records),
            "mean_recall_at_k": statistics.mean(r["retrieval"]["recall_at_k"] for r in records),
            "mean_mrr": statistics.mean(r["retrieval"]["mrr"] for r in records),
        },
    }
    if not dry_run:
        escalation_correct = [r["escalation_correct"] for r in records]
        agg["escalation_accuracy"] = sum(escalation_correct) / len(escalation_correct)

        judged = [r["judge_scores"] for r in records if "judge_scores" in r]
        if judged:
            dims = ["answer_relevance", "factual_accuracy", "completeness", "reasoning_clarity", "domain_specificity"]
            agg["fab_bench_scores"] = {
                dim: statistics.mean(j[dim] for j in judged) for dim in dims
            }
            agg["fab_bench_scores"]["overall_mean"] = statistics.mean(
                statistics.mean(j[dim] for dim in dims) for j in judged
            )
    return agg


def _print_report(report: dict[str, Any], dry_run: bool) -> None:
    print(f"\n=== Continuity eval report ({'dry-run, retrieval only' if dry_run else 'full'}) ===")
    print(f"Scenarios: {report['n_scenarios']}")
    r = report["retrieval"]
    print(f"Retrieval  — precision@k: {r['mean_precision_at_k']:.2f}  recall@k: {r['mean_recall_at_k']:.2f}  MRR: {r['mean_mrr']:.2f}")
    if not dry_run:
        print(f"Escalation accuracy (correctly identifying knowledge-base gaps): {report['escalation_accuracy']:.2f}")
        if "fab_bench_scores" in report:
            fb = report["fab_bench_scores"]
            print("FAB-Bench-style scores (1-5, LLM-judged against reference answers):")
            for k, v in fb.items():
                print(f"  {k}: {v:.2f}")
    print(f"Full per-scenario results written to eval_results.json\n")
