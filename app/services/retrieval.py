from __future__ import annotations

from typing import TypedDict


class RetrievedChunk(TypedDict):
    anchor: str
    source: str
    path: str
    snippet_start: int
    snippet: str
    score: float


def retrieve(query: str, top_k: int = 6) -> list[RetrievedChunk]:
    """
    TODO: hook to real index. For now return [] safely.
    Must never raise on empty corpus; contract consumers rely on that.
    """
    return []
