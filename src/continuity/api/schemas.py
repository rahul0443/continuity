from __future__ import annotations

from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    query: str = Field(..., min_length=5, description="Shift engineer's fault description")
    equipment: str | None = Field(default=None, description="Equipment name/ID, if known")


class Cause(BaseModel):
    cause: str
    confidence: str
    cited_sources: list[str]
    recommended_action: str


class DiagnoseResponse(BaseModel):
    escalated: bool
    summary: str | None = None
    causes: list[Cause] = []
    escalation_message: str | None = None
    retrieved_sources: list[str] = []


class ResolveCaseRequest(BaseModel):
    query: str
    equipment: str | None = None
    resolution_summary: str = Field(..., min_length=3)
    resolved_by: str | None = None


class ResolveCaseResponse(BaseModel):
    status: str
    doc_id: str
