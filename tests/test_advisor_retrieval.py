from app.schemas.advisor import AdvisorQuery
from app.services import retrieval
from app.services.advisor_orchestrator import stream_advisor_answer


def test_retrieval_returns_anchors(monkeypatch):
    fake = [
        {
            "anchor": "§1.4.5",
            "source": "PRD_v4.0_unified_numbered.md",
            "path": "docs/PRD/PRD_v4.0_unified_numbered.md",
            "snippet_start": 10,
            "snippet": "Advisor requirements include sources...",
            "score": 1.0,
        },
        {
            "anchor": "§ext-foundryhr.foo",
            "source": "ext-foundryhr/file.md",
            "path": "knowledge_base/sources/ext-foundryhr/file.md",
            "snippet_start": 0,
            "snippet": "External KB rule...",
            "score": 0.9,
        },
    ]
    monkeypatch.setattr(retrieval, "retrieve", lambda q, top_k=6: fake)
    from app.retrieval import ollama_client

    def fake_chat(*args, **kwargs):
        yield {"text": "Hello "}
        yield {"text": "world."}

    monkeypatch.setattr(ollama_client, "chat", lambda **kw: fake_chat())
    q = AdvisorQuery(query="How do we enforce citations?", top_k=2)
    gen = stream_advisor_answer(q, "adv_test")
    events = list(gen)
    final = next(e for e in events if e.get("event") == "final")
    cits = final["answer"]["citations"]
    assert len(cits) == 2
    assert cits[0]["anchor"] == "§1.4.5"
    assert cits[1]["anchor"].startswith("§ext-")


def test_no_citations_tag(monkeypatch):
    monkeypatch.setattr(retrieval, "retrieve", lambda q, top_k=6: [])
    from app.retrieval import ollama_client

    monkeypatch.setattr(ollama_client, "chat", lambda **kw: iter([{"text": "ok"}]))
    events = list(stream_advisor_answer(AdvisorQuery(query="x"), "adv_x"))
    final = next(e for e in events if e.get("event") == "final")
    assert final["answer"]["explainability_tag"] == "no_citation_context"
