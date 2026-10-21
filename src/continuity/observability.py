"""Structured JSON logging and per-stage latency timing.

Every pipeline stage (retrieve, triage, answer, escalate) runs inside
``timed_stage``, which emits one JSON log line with the stage name, wall-clock
latency in milliseconds, and any extra fields the caller attaches. JSON lines
are easy to ship to any log aggregator and to query by stage or request.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

logger = logging.getLogger("continuity")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = _request_id.get()
        if rid:
            payload["request_id"] = rid
        extra = getattr(record, "fields", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    """Idempotent: attaches one JSON handler to the 'continuity' logger."""
    if any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        logger.setLevel(level)
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False


def new_request_id() -> str:
    rid = uuid.uuid4().hex[:12]
    _request_id.set(rid)
    return rid


def log_event(message: str, **fields: Any) -> None:
    logger.info(message, extra={"fields": fields})


@contextmanager
def timed_stage(stage: str, **fields: Any) -> Iterator[dict[str, Any]]:
    """Times a pipeline stage and logs one JSON line when it finishes.

    The yielded dict lets the caller attach result fields (for example the
    number of chunks retrieved) that are included in the log line. If the
    stage raises, the line is logged with status "error" and the exception
    type, and the exception propagates unchanged.
    """
    extra: dict[str, Any] = dict(fields)
    start = time.perf_counter()
    status = "ok"
    try:
        yield extra
    except Exception as exc:
        status = "error"
        extra["error_type"] = type(exc).__name__
        raise
    finally:
        extra["stage"] = stage
        extra["status"] = status
        extra["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"stage_complete:{stage}", extra={"fields": extra})
