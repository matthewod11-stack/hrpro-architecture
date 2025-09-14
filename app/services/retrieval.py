from __future__ import annotations

from typing import TypedDict

from app.retrieval.adapter import retrieve as adapter_retrieve


class RetrievedChunk(TypedDict):
    anchor: str
    source: str
    path: str
    snippet_start: int
    snippet: str
    score: float


def retrieve(query: str, top_k: int = 6) -> list[RetrievedChunk]:
    """Retrieve chunks related to a query.

    Uses the retrieval adapter and normalizes the results into the
    ``RetrievedChunk`` structure. The contract guarantees that this
    function never raises; if anything goes wrong an empty list is
    returned so upstream callers can handle missing context gracefully.
    """

    try:
        raw_results = adapter_retrieve(query, top_k)
    except Exception:
        # Maintain contract: never raise on failure
        return []

    chunks: list[RetrievedChunk] = []
    for r in raw_results:
        chunk: RetrievedChunk = {
            "anchor": r.get("anchor", ""),
            "source": r.get("doc", ""),
            "path": r.get("path", ""),
            "snippet_start": r.get("snippet_start", 0),
            "snippet": r.get("snippet", ""),
            "score": float(r.get("score", 0.0)),
        }
        chunks.append(chunk)

    return chunks
