import json
from pathlib import Path

import requests
import yaml

# Load config
with open("config/retrieval.yaml") as f:
    cfg = yaml.safe_load(f)
endpoint = cfg.get("ollama", {}).get("endpoint", "http://localhost:11434")
model = cfg.get("ollama", {}).get("model", "phi3:latest")

corpus_path = Path("knowledge_base/corpus.jsonl")
rows = [json.loads(line) for line in corpus_path.open()]

aliases = {}


def prompt(section, text):
    instr = f"""
Given the following section heading and text, produce:
- normalized_title: a concise, kebab-case version of the heading
- anchor_suggestion: ext-<normalized_title>
- aliases: 2–5 plausible variants or synonyms for the heading

Section: {section}
Text: {text[:400]}

Respond as JSON:
{{"normalized_title":..., "anchor_suggestion":..., "aliases":[...]}}
"""
    resp = requests.post(
        f"{endpoint}/api/generate",
        json={"model": model, "prompt": instr, "stream": False},
        timeout=30,
    )
    resp.raise_for_status()
    out = resp.json()["response"]
    try:
        j = json.loads(out)
        return j
    except Exception:
        return None


for r in rows:
    if r.get("workspace") == "external":
        section = r.get("section", "")
        text = r.get("text", "")
        anchor = r.get("anchor", "")
        res = prompt(section, text)
        if res and "aliases" in res:
            aliases[anchor] = res["aliases"]

with open("knowledge_base/anchor_aliases.json", "w") as f:
    json.dump(aliases, f, indent=2)

print(f"Normalized {len(aliases)} external anchors with aliases.")
