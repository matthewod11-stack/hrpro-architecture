from __future__ import annotations

from collections.abc import Iterator
import json
import time

from app.retrieval import ollama_client
from app.schemas.advisor import AdvisorAnswer, AdvisorQuery, Citation
from app.services import retrieval
from app.services.telemetry import emit


def _compose_system_prompt(persona: str) -> str:
    # TODO: load CPO persona from file/env; basic guard for now
    return (
        "You are HRPro's Chief People Officer. Cite sources with exact anchors (e.g., §1.4.5). "
        "If uncertain, say so. Respond ONLY with valid JSON containing keys: summary (string), findings (array of strings), "
        "actions (array of strings), and insights (array of strings)."
    )


def _context_block(chunks) -> str:
    if not chunks:
        return "[CONTEXT]\n(no retrieved context)"
    lines = [f"{i+1}) {c['anchor']} — {c['snippet']}" for i, c in enumerate(chunks)]
    return "[CONTEXT]\n" + "\n".join(lines) + "\nRules: Cite using exact anchors."


def stream_advisor_answer(q: AdvisorQuery, trace_id: str) -> Iterator[dict]:
    emit("advisor", {"event": "start", "trace_id": trace_id, "query_len": len(q.query)})
    t0 = time.perf_counter()
    ttfa_emitted = False

    chunks = retrieval.retrieve(q.query, top_k=q.top_k)
    user_prompt = f"{_context_block(chunks)}\n\n[USER]\n{q.query}"
    system_prompt = _compose_system_prompt(q.persona)

    buffer = []

    try:
        model = (q.context or {}).get("model", "llama3.1:8b")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        resp = ollama_client.chat(model=model, messages=messages, stream=True)

        # Support both streaming iterators and single dict responses
        if isinstance(resp, dict):
            iterator = [resp]
        else:
            iterator = resp

        for part in iterator:
            chunk = part.get("message", part.get("response", ""))
            if isinstance(chunk, dict):
                chunk = chunk.get("content", "")
            if not chunk:
                continue
            buffer.append(chunk)
            if not ttfa_emitted:
                ttfa = int((time.perf_counter() - t0) * 1000)
                emit("advisor", {"event": "ttfa", "trace_id": trace_id, "ms": ttfa})
                ttfa_emitted = True
            yield {
                "event": "delta",
                "text": chunk,
                "trace_id": trace_id,
            }

        full = "".join(buffer).strip()
        try:
            payload = json.loads(full)
        except Exception:
            payload = {"summary": full, "findings": [], "actions": [], "insights": []}

        citations = [
            Citation(
                anchor=c["anchor"],
                source=c["source"],
                path=c["path"],
                snippet_start=int(c.get("snippet_start", 0)),
                snippet=(c.get("snippet", "") or "").replace("\n", " ")[:200],
            )
            for c in chunks
        ]

        tag = "cpo.v1"
        if not citations:
            tag = "no_citation_context"

        answer = AdvisorAnswer(
            summary=payload.get("summary", ""),
            findings=payload.get("findings", []),
            actions=payload.get("actions", []),
            insights=payload.get("insights", []),
            citations=citations,
            explainability_tag=tag,
            trace_id=trace_id,
        )

        emit(
            "advisor",
            {
                "event": "final",
                "trace_id": trace_id,
                "has_citations": bool(citations),
                "token_len": len(full),
                "total_ms": int((time.perf_counter() - t0) * 1000),
            },
        )
        yield {
            "event": "final",
            "answer": answer.model_dump(),
            "trace_id": trace_id,
        }
    except Exception as e:
        # emit error event
        yield {
            "event": "error",
            "message": str(e),
            "trace_id": trace_id,
        }
        # emit a final event with empty answer to guarantee contract
        answer = AdvisorAnswer(
            summary="",
            findings=[],
            actions=[],
            insights=[],
            citations=[],
            explainability_tag="error",
            trace_id=trace_id,
        )
        yield {
            "event": "final",
            "answer": answer.model_dump(),
            "trace_id": trace_id,
        }
