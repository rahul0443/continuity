"""Side-effecting tools the agent graph calls: writing a detected knowledge
gap out for follow-up, and writing a resolved case back into the knowledge
base. Both append to plain JSONL files rather than a database — appropriate
for a PoC's scope; a production handoff would replace these with real
persistence (see README "Path to production").
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from continuity.config import settings
from continuity.retrieval.chunking import Chunk
from continuity.retrieval.vectorstore import get_client, get_collection, index_chunks


def flag_knowledge_gap(query: str, equipment: str | None, reasoning: str) -> dict:
    """Logs a fault description the knowledge base could not ground a
    diagnosis for. This is the tool's literal operationalization of the
    problem it exists to address: instead of silently guessing, it records
    exactly where institutional knowledge is currently missing, so it can be
    prioritized for the next knowledge-capture interview."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "equipment": equipment,
        "triage_reasoning": reasoning,
    }
    settings.knowledge_gaps_path.parent.mkdir(parents=True, exist_ok=True)
    with settings.knowledge_gaps_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def log_resolved_case(
    query: str,
    resolution_summary: str,
    equipment: str | None = None,
    resolved_by: str | None = None,
    reindex: bool = True,
) -> dict:
    """Appends a resolved case to the write-back log and, by default,
    immediately re-indexes it into the live Chroma collection so the next
    query can retrieve it — this is the "institutional knowledge accumulates
    instead of leaving with rotating staff" loop from the project thesis,
    scoped down to a simple confirm-and-save action rather than a retraining
    pipeline."""
    timestamp = datetime.now(timezone.utc).isoformat()
    doc_id = f"LEARNED-{int(datetime.now(timezone.utc).timestamp())}"
    record = {
        "timestamp": timestamp,
        "doc_id": doc_id,
        "query": query,
        "resolution_summary": resolution_summary,
        "equipment": equipment or "unspecified",
        "resolved_by": resolved_by or "unspecified",
    }
    settings.learned_cases_path.parent.mkdir(parents=True, exist_ok=True)
    with settings.learned_cases_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    if reindex:
        chunk = Chunk(
            chunk_id=f"{doc_id}::0",
            doc_id=doc_id,
            equipment=record["equipment"],
            doc_type="learned_case",
            title=f"Resolved case: {query[:60]}",
            section="Resolution",
            text=(
                f"[learned_case] Resolved case ({record['equipment']}) — Resolution\n\n"
                f"Fault description: {query}\n\nResolution: {resolution_summary}"
            ),
        )
        client = get_client(settings.chroma_persist_dir)
        collection = get_collection(client)
        index_chunks(collection, [chunk])

    return record
