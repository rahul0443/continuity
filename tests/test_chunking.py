from continuity.config import settings
from continuity.retrieval.chunking import load_corpus


def test_load_corpus_finds_all_synthetic_docs():
    chunks = load_corpus(settings.data_dir)
    assert len(chunks) > 0
    doc_ids = {c.doc_id for c in chunks}
    # 5 SOPs + 10 incident logs + 5 knowledge-capture interviews = 20 docs
    assert len(doc_ids) == 20


def test_chunks_have_required_metadata():
    chunks = load_corpus(settings.data_dir)
    for c in chunks[:5]:
        assert c.doc_id
        assert c.equipment
        assert c.doc_type in {"SOP", "incident_log", "knowledge_capture_interview"}
        assert c.text.strip()
