"""Verifies /api/diagnose surfaces upstream Anthropic errors as a clean 502
with the real error message, instead of falling through to FastAPI's
generic, undiagnosable 500 — this was the actual gap that made a live
deployment failure impossible to diagnose from outside the host's logs."""
from __future__ import annotations

import anthropic
import pytest
from fastapi.testclient import TestClient

from continuity.api.main import app
from continuity.llm import MissingAPIKeyError

client = TestClient(app)


def _fake_api_error():
    request = __import__("httpx").Request("POST", "https://api.anthropic.com/v1/messages")
    return anthropic.APIStatusError(
        "invalid x-api-key", response=__import__("httpx").Response(401, request=request), body=None
    )


def test_missing_api_key_returns_503(monkeypatch):
    def raise_missing(*_args, **_kwargs):
        raise MissingAPIKeyError("no key configured")

    monkeypatch.setattr("continuity.api.routes.run_continuity_agent", raise_missing)
    resp = client.post("/api/diagnose", json={"query": "fault description long enough"})
    assert resp.status_code == 503


def test_upstream_anthropic_error_returns_502_not_bare_500(monkeypatch):
    def raise_api_error(*_args, **_kwargs):
        raise _fake_api_error()

    monkeypatch.setattr("continuity.api.routes.run_continuity_agent", raise_api_error)
    resp = client.post("/api/diagnose", json={"query": "fault description long enough"})
    assert resp.status_code == 502
    assert "Upstream Anthropic API error" in resp.json()["detail"]
