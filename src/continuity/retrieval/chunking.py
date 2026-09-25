"""Parses the synthetic markdown corpus (SOPs, incident logs, knowledge-capture
interviews) into retrievable chunks, splitting each document on its `##`
section headers so a retrieved chunk maps to one coherent procedure step or
incident section rather than a whole multi-page document.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    equipment: str
    doc_type: str
    title: str
    section: str
    text: str


def parse_document(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {path}")
    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()
    return meta, body


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split a markdown body into (heading, text) pairs on '## ' headers.

    Everything before the first '## ' header (the H1 title and any summary
    lines) is kept as an "Overview" section rather than dropped.
    """
    sections: list[tuple[str, str]] = []
    heading = "Overview"
    buffer: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if buffer:
                sections.append((heading, "\n".join(buffer).strip()))
            heading = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    if buffer:
        sections.append((heading, "\n".join(buffer).strip()))
    return [(h, t) for h, t in sections if t]


def load_corpus(data_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(data_dir.rglob("*.md")):
        meta, body = parse_document(path)
        doc_id = meta["doc_id"]
        title = meta.get("title", doc_id)
        equipment = meta.get("equipment", "unknown")
        doc_type = meta.get("doc_type", "unknown")
        for i, (heading, text) in enumerate(split_sections(body)):
            chunk_text = f"[{doc_type}] {title} ({equipment}) — {heading}\n\n{text}"
            chunks.append(
                Chunk(
                    chunk_id=f"{doc_id}::{i}",
                    doc_id=doc_id,
                    equipment=equipment,
                    doc_type=doc_type,
                    title=title,
                    section=heading,
                    text=chunk_text,
                )
            )
    return chunks
