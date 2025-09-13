import json
import os
from pathlib import Path
import time

from fastapi import APIRouter
from pydantic import BaseModel

from app.advisor.prompts import get_cpo_system_prompt
from app.retrieval import ollama_client
from app.retrieval.adapter import retrieve

router = APIRouter()


class AdvisorAnswerRequest(BaseModel):
    organization: str
    topic: str
    top_k: int = 5


@router.post("/v1/advisor/answer")
async def advisor_answer(req: AdvisorAnswerRequest):
    t0 = time.time()
    model = os.getenv("OLLAMA_MODEL_GENERAL", "llama3.1:8b")
    # require_citations = os.getenv("REQUIRE_CITATIONS", "true").lower() == "true"  # Removed unused variable
    backend = os.getenv("ADVISOR_BACKEND", "ollama")
    snippets = retrieve(req.topic, req.top_k)
    retrieved_docs_count = len(snippets)
    if retrieved_docs_count == 0:
        reason = "No relevant local documents found; refusing per grounding policy."
        _log_telemetry(
            ttfa_ms=int((time.time() - t0) * 1000), has_citations=False, count=0
        )
        return {
            "answer_text": None,
            "source_attributions": [],
            "guardrail_reason": reason,
            "metrics": {
                "advisor_ttfa_ms": int((time.time() - t0) * 1000),
                "advisor_has_citations": False,
                "retrieved_docs_count": 0,
            },
        }
    # Prompt assembly
    system = get_cpo_system_prompt(req.organization)
    context_lines = []
    for i, s in enumerate(snippets, 1):
        context_lines.append(
            f"[{i}] {s['anchor']} — {s['section']}\npath: {s['path']}\n---\n{s['snippet'][:320]}"
        )
    user = f"Topic: {req.topic}\nContext:\n" + "\n\n".join(context_lines)
    user += "\nInstructions: Answer strictly using the provided context. If context is insufficient, say you cannot answer and specify what is missing. Structure output per <output_specifications>."
    answer_text = None
    guardrail_reason = None
    if backend == "heuristic":
        answer_text = f"Summary: {req.topic}. Sources: " + ", ".join(
            [s["anchor"] for s in snippets]
        )
    else:
        try:
            resp = ollama_client.chat(
                model,
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                stream=False,
            )
            answer_text = resp.get("message", resp.get("response", ""))
        except Exception as e:
            answer_text = None
            guardrail_reason = f"Model error: {str(e)}"
    # Attributions (simple: top-K)
    source_attributions = (
        [
            {"anchor": s["anchor"], "section": s["section"], "path": s["path"]}
            for s in snippets
        ]
        if answer_text
        else []
    )
    has_citations = bool(source_attributions)
    _log_telemetry(
        ttfa_ms=int((time.time() - t0) * 1000),
        has_citations=has_citations,
        count=retrieved_docs_count,
    )
    return {
        "answer_text": answer_text,
        "source_attributions": source_attributions,
        "guardrail_reason": guardrail_reason,
        "metrics": {
            "advisor_ttfa_ms": int((time.time() - t0) * 1000),
            "advisor_has_citations": has_citations,
            "retrieved_docs_count": retrieved_docs_count,
        },
    }


def _log_telemetry(ttfa_ms, has_citations, count):
    path = Path("logs/dev_telemetry.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "event": "advisor_answer",
            "advisor_ttfa_ms": ttfa_ms,
            "advisor_has_citations": has_citations,
            "retrieved_docs_count": count,
            "ts": int(time.time() * 1000),
        }
    )
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
