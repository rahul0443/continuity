from __future__ import annotations

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

    retrieved_sources = [r.chunk.doc_id for r in result.get("retrieved", [])]

    if result.get("escalated"):
        return DiagnoseResponse(
            escalated=True,
            escalation_message=result["escalation"]["message"],
            retrieved_sources=retrieved_sources,
        )

    answer = result["answer"]
    return DiagnoseResponse(
        escalated=False,
        summary=answer.get("summary"),
        causes=[Cause(**c) for c in answer.get("causes", [])],
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
