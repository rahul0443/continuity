#!/usr/bin/env python
"""CI gate: fail if retrieval metrics regress against the committed baseline.

  python scripts/run_eval.py --dry-run --out /tmp/report.json
  python scripts/check_regression.py --report /tmp/report.json
"""
import argparse
import sys

from continuity.eval.regression import check_regression, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="Dry-run eval report JSON.")
    parser.add_argument("--baseline", default="data/eval/retrieval_baseline.json")
    parser.add_argument("--tolerance", type=float, default=0.02)
    args = parser.parse_args()

    failures = check_regression(load_json(args.report), load_json(args.baseline), args.tolerance)
    if failures:
        print("Retrieval regression gate FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Retrieval regression gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
