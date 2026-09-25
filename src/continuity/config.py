import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Silence chromadb's anonymized telemetry (a harmless posthog call that
# throws a noisy but non-fatal exception in some chromadb/posthog version
# combinations) — set before chromadb is imported anywhere.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

# src/continuity/config.py -> parents[2] is the project root (continuity/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "synthetic")
    eval_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "eval")
    chroma_persist_dir: Path = field(default_factory=lambda: PROJECT_ROOT / ".chroma")
    knowledge_gaps_path: Path = field(
        default_factory=lambda: PROJECT_ROOT / "data" / "knowledge_gaps.jsonl"
    )
    learned_cases_path: Path = field(
        default_factory=lambda: PROJECT_ROOT / "data" / "learned_cases.jsonl"
    )
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    )
    retrieval_top_k: int = field(default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "5")))
    min_fused_score_threshold: float = field(
        default_factory=lambda: float(os.getenv("MIN_FUSED_SCORE_THRESHOLD", "0.02"))
    )


settings = Settings()
