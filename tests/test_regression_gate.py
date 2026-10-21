import json
from pathlib import Path

from continuity.eval.regression import check_regression

BASELINE = {
    "n_scenarios": 16,
    "retrieval": {"mean_precision_at_k": 0.5875, "mean_recall_at_k": 0.9375, "mean_mrr": 0.7083},
}


def _report(p=0.5875, r=0.9375, m=0.7083, n=16):
    return {
        "n_scenarios": n,
        "retrieval": {"mean_precision_at_k": p, "mean_recall_at_k": r, "mean_mrr": m},
    }


def test_identical_report_passes():
    assert check_regression(_report(), BASELINE) == []


def test_small_drop_within_tolerance_passes():
    assert check_regression(_report(r=0.93), BASELINE) == []


def test_recall_drop_beyond_tolerance_fails():
    failures = check_regression(_report(r=0.85), BASELINE)
    assert len(failures) == 1
    assert "mean_recall_at_k" in failures[0]


def test_improvement_passes():
    assert check_regression(_report(p=0.7, r=0.95, m=0.8), BASELINE) == []


def test_scenario_count_change_fails():
    failures = check_regression(_report(n=15), BASELINE)
    assert any("scenario count" in f for f in failures)


def test_committed_baseline_matches_committed_eval_results():
    root = Path(__file__).resolve().parents[1]
    baseline = json.loads((root / "data/eval/retrieval_baseline.json").read_text())
    results = json.loads((root / "eval_results.json").read_text())
    assert check_regression(results, baseline, tolerance=0.0) == []
