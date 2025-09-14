import json
import os
from pathlib import Path
import re

import yaml

from app.retrieval import ollama_client
from app.services import telemetry


def _log_event(event, **kwargs):
    telemetry.emit("retrieval", {"event": event, **kwargs})


def _extract_json(text):
    m = re.search(r"{.*}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _heuristic(prompt, aliases_map):
    aliases = []
    if aliases_map:
        for v in aliases_map.values():
            aliases.extend(v)
    aliases = list(dict.fromkeys(aliases))
    expanded_query = prompt + " " + " ".join(aliases[:3])
    must_have = re.findall(r"\b\w+\b", prompt)[:3]
    nice_to_have = [a for a in aliases[:5] if a not in must_have]
    _log_event("query_rewrite", backend="heuristic", must=must_have, nice=nice_to_have)
    return {
        "expanded_query": expanded_query,
        "must_have": must_have,
        "nice_to_have": nice_to_have,
    }


def rewrite(prompt: str, aliases_map: dict = None) -> dict:
    # Load config/model
    model = None
    config_path = Path(__file__).parent.parent.parent / "config/retrieval.yaml"
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        model = cfg.get("OLLAMA_MODEL_REWRITE") or cfg.get("ollama", {}).get("model")
    if not model:
        model = os.environ.get("OLLAMA_MODEL_REWRITE", "llama3.1:8b")
    # Aliases
    flat_aliases = []
    if aliases_map:
        for v in aliases_map.values():
            flat_aliases.extend(v)
    flat_aliases = list(dict.fromkeys(flat_aliases))
    # Compose messages
    system = (
        "You rewrite HR/engineering queries into keyword bundles. "
        "Return strictly JSON with keys: expanded_query, must_have (2-4 single-word or bigram terms), "
        "nice_to_have (0-5). Keep within domain; avoid hallucinations."
    )
    user = f"Original topic: {prompt}\nAliases (optional): {', '.join(flat_aliases)}"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    # Try chat
    try:
        resp = ollama_client.chat(model, messages, stream=False)
        out = resp.get("message", resp.get("response", ""))
        j = _extract_json(out)
        if j and all(k in j for k in ("expanded_query", "must_have", "nice_to_have")):
            _log_event(
                "query_rewrite",
                backend="ollama",
                must=j["must_have"],
                nice=j["nice_to_have"],
            )
            return j
        else:
            _log_event("rewrite_json_invalid", backend="ollama", raw=out[:200])
    except Exception:
        pass
    # Fallback: generate
    try:
        gen_prompt = system + "\n\n" + user
        resp = ollama_client.generate(model, gen_prompt, stream=False)
        out = resp.get("response", "")
        j = _extract_json(out)
        if j and all(k in j for k in ("expanded_query", "must_have", "nice_to_have")):
            _log_event(
                "query_rewrite",
                backend="generate",
                must=j["must_have"],
                nice=j["nice_to_have"],
            )
            return j
        else:
            _log_event("rewrite_json_invalid", backend="generate", raw=out[:200])
    except Exception:
        pass
    # Final fallback: heuristic
    return _heuristic(prompt, aliases_map)
