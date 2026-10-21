import json
import logging

import pytest

from continuity.observability import JsonFormatter, configure_logging, new_request_id, timed_stage


@pytest.fixture
def captured():
    logger = logging.getLogger("continuity")
    records: list[str] = []

    class ListHandler(logging.Handler):
        def emit(self, record):
            records.append(self.format(record))

    handler = ListHandler()
    handler.setFormatter(JsonFormatter())
    old_level, old_prop = logger.level, logger.propagate
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    yield records
    logger.removeHandler(handler)
    logger.setLevel(old_level)
    logger.propagate = old_prop


def test_timed_stage_logs_one_json_line_with_latency(captured):
    with timed_stage("retrieve") as log:
        log["n_chunks"] = 5
    assert len(captured) == 1
    line = json.loads(captured[0])
    assert line["stage"] == "retrieve"
    assert line["status"] == "ok"
    assert line["n_chunks"] == 5
    assert line["latency_ms"] >= 0


def test_timed_stage_logs_error_and_reraises(captured):
    with pytest.raises(ValueError):
        with timed_stage("answer"):
            raise ValueError("boom")
    line = json.loads(captured[0])
    assert line["status"] == "error"
    assert line["error_type"] == "ValueError"


def test_request_id_is_attached(captured):
    rid = new_request_id()
    with timed_stage("triage"):
        pass
    assert json.loads(captured[0])["request_id"] == rid


def test_configure_logging_is_idempotent():
    logger = logging.getLogger("continuity")
    before = len(logger.handlers)
    configure_logging()
    configure_logging()
    assert len(logger.handlers) <= before + 1
