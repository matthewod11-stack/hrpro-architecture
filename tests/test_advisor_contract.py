from app.schemas.advisor import AdvisorAnswer


def test_final_payload_schema_roundtrip():
    payload = {
        "summary": "s",
        "findings": ["f1"],
        "actions": ["a1"],
        "insights": ["i1"],
        "citations": [
            {
                "anchor": "§1.4.5",
                "source": "PRD.md",
                "path": "docs/PRD.md",
                "snippet_start": 0,
                "snippet": "...",
            }
        ],
        "explainability_tag": "cpo.v1",
        "trace_id": "adv_x",
    }
    ans = AdvisorAnswer(**payload)
    enc = ans.model_dump()
    assert enc["trace_id"] == "adv_x"
    assert enc["citations"][0]["anchor"].startswith("§")
