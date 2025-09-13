import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")

from app.retrieval import ollama_client


def test_chat_payload(monkeypatch):
    called = {}

    def fake_post(url, json=None, timeout=None):
        called["url"] = url
        called["json"] = json
        called["timeout"] = timeout

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "message": '{"expanded_query": "foo", "must_have": ["bar"], "nice_to_have": ["baz"]}'
                }

        return Resp()

    monkeypatch.setattr("requests.post", fake_post)
    model = "llama3.1:8b"
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "user"},
    ]
    result = ollama_client.chat(model, messages, stream=False)
    assert called["url"].endswith("/api/chat")
    assert called["json"]["model"] == model
    assert called["json"]["messages"] == messages
    assert called["json"]["stream"] is False
    assert isinstance(result, dict)


def test_generate_payload(monkeypatch):
    called = {}

    def fake_post(url, json=None, timeout=None):
        called["url"] = url
        called["json"] = json
        called["timeout"] = timeout

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "response": '{"expanded_query": "foo", "must_have": ["bar"], "nice_to_have": ["baz"]}'
                }

        return Resp()

    monkeypatch.setattr("requests.post", fake_post)
    model = "llama3.1:8b"
    prompt = "hello"
    result = ollama_client.generate(model, prompt, stream=False)
    assert called["url"].endswith("/api/generate")
    assert called["json"]["model"] == model
    assert called["json"]["prompt"] == prompt
    assert called["json"]["stream"] is False
    assert isinstance(result, dict)


def test_log_event(tmp_path, monkeypatch):
    log_path = tmp_path / "dev_telemetry.jsonl"
    monkeypatch.setattr(ollama_client, "LOG_PATH", log_path)
    ollama_client._log_event(
        "ollama_http_error",
        endpoint="/api/chat",
        status=400,
        model="llama3.1:8b",
        trunc_payload="...",
        err="bad",
    )
    lines = log_path.read_text().splitlines()
    assert any("ollama_http_error" in line for line in lines)
