"""Retrieval regression gate.

Compares a fresh dry-run eval report against a committed baseline and fails
if any retrieval metric drops by more than the allowed tolerance. Retrieval
metrics are deterministic (no LLM involved), so a drop means a real change in
chunking, embeddings, fusion or reranking, not sampling noise.
"""
from __future__ import annotations

import json
from pathlib import Path

METRICS = ("mean_precision_at_k", "mean_recall_at_k", "mean_mrr")


def check_regression(report: dict, baseline: dict, tolerance: float = 0.02) -> list[str]:
    """Returns a list of human-readable failures (empty means the gate passes)."""
    failures: list[str] = []
    if report.get("n_scenarios") != baseline.get("n_scenarios"):
        failures.append(
            f"scenario count changed: baseline {baseline.get('n_scenarios')}, report {report.get('n_scenarios')}"
        )
    for metric in METRICS:
        base = baseline["retrieval"][metric]
        new = report["retrieval"][metric]
        if new < base - tolerance:
            failures.append(f"{metric} regressed: baseline {base:.4f}, now {new:.4f} (tolerance {tolerance})")
    return failures


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
