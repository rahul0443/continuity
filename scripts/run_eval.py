#!/usr/bin/env python
"""CLI entry point for the eval harness.

  python scripts/run_eval.py --dry-run     # retrieval metrics only, no API key needed
  python scripts/run_eval.py               # full agent + FAB-Bench-style LLM-judge scoring
"""
import argparse

from continuity.eval.harness import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only compute retrieval metrics against ground truth; skips agent generation and LLM-judge scoring (no ANTHROPIC_API_KEY needed).",
    )
    parser.add_argument("--out", default="eval_results.json", help="Where to write the full JSON report.")
    args = parser.parse_args()
    run_eval(dry_run=args.dry_run, out_path=args.out)


if __name__ == "__main__":
    main()
