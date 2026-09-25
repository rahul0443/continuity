#!/usr/bin/env python
"""Chunks the synthetic corpus and (re)builds the persistent Chroma index.

Run this once before starting the API/UI, and again any time files under
data/synthetic/ change.
"""
from continuity.config import settings
from continuity.retrieval.chunking import load_corpus
from continuity.retrieval.vectorstore import get_client, get_collection, index_chunks


def main() -> None:
    chunks = load_corpus(settings.data_dir)
    if not chunks:
        raise SystemExit(f"No documents found under {settings.data_dir}")
    client = get_client(settings.chroma_persist_dir)
    collection = get_collection(client)
    n = index_chunks(collection, chunks)
    by_type: dict[str, int] = {}
    for c in chunks:
        by_type[c.doc_type] = by_type.get(c.doc_type, 0) + 1
    print(f"Indexed {n} chunks into {settings.chroma_persist_dir}")
    print(f"By doc_type: {by_type}")


if __name__ == "__main__":
    main()
