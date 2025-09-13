from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AdvisorQuery(BaseModel):
    query: str
    persona: Literal["cpo"] = "cpo"
    top_k: int = 6
    workspace: str | None = None
    context: dict[str, Any] | None = None


class Citation(BaseModel):
    anchor: str  # e.g. "§1.4.5" or "§ext-<ns>.<slug>"
    source: str  # display name (filename)
    path: str  # repo-relative path
    snippet_start: int = 0
    snippet: str = ""


class AdvisorAnswer(BaseModel):
    summary: str
    findings: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    explainability_tag: str = "cpo.v1"
    trace_id: str
