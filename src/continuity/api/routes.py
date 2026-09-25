from __future__ import annotations

import anthropic
from fastapi import APIRouter, HTTPException

from continuity.agent.graph import run_continuity_agent
from continuity.agent.tools import log_resolved_case
from continuity.api.schemas import (
    Cause,
    DiagnoseRequest,
    DiagnoseResponse,
    ResolveCaseRequest,
    ResolveCaseResponse,
)
from continuity.llm import MissingAPIKeyError

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(req: DiagnoseRequest) -> DiagnoseResponse:
    try:
        result = run_continuity_agent(req.query, req.equipment)
    except MissingAPIKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except anthropic.APIError as exc:
        # Surface the real upstream error (bad/expired key, rate limit, quota,
        # transient outage) instead of letting it fall through to FastAPI's
        # generic, undiagnosable "Internal Server Error" — this was previously
        # unhandled and is exactly what made a live-deployment failure
        # impossible to diagnose from outside the host's own logs.
        raise HTTPException(status_code=502, detail=f"Upstream Anthropic API error: {exc}") from exc

    retrieved_sources = [r.chunk.doc_id for r in result.get("retrieved", [])]

    if result.get("escalated"):
        return DiagnoseResponse(
            escalated=True,
            escalation_message=result["escalation"]["message"],
            retrieved_sources=retrieved_sources,
        )

    answer = result["answer"]
    causes: list[Cause] = []
    for c in answer.get("causes", []):
        try:
            causes.append(Cause(**c))
        except (TypeError, ValueError):
            # continuity.llm's schema-driven coercion repairs the malformed
            # tool-call shapes observed in practice, but LLM output is
            # fundamentally non-deterministic — drop a residual unparseable
            # cause rather than 500 the whole response over one of several.
            continue

    return DiagnoseResponse(
        escalated=False,
        summary=answer.get("summary"),
        causes=causes,
        retrieved_sources=retrieved_sources,
    )


@router.post("/cases/resolve", response_model=ResolveCaseResponse)
def resolve_case(req: ResolveCaseRequest) -> ResolveCaseResponse:
    record = log_resolved_case(
        query=req.query,
        resolution_summary=req.resolution_summary,
        equipment=req.equipment,
        resolved_by=req.resolved_by,
    )
    return ResolveCaseResponse(status="logged", doc_id=record["doc_id"])
