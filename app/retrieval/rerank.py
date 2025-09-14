import numpy as np
import requests
import yaml

from app.services.telemetry import emit


def ollama_rerank(query, candidates):
    with open("config/retrieval.yaml") as f:
        cfg = yaml.safe_load(f)
    endpoint = cfg.get("ollama", {}).get("endpoint", "http://localhost:11434")
    model = cfg.get("ollama", {}).get("model", "phi3:latest")
    try:
        passages = [f"{c['section']}\n{c['snippet'][:400]}" for c in candidates]
        payload = {
            "model": model,
            "query": query,
            "passages": passages,
            "stream": False,
        }
        resp = requests.post(
            f"{endpoint}/api/generate", json=payload, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        responses = data.get("responses", [])
        scores = [float(r.strip()) for r in responses]
        if len(scores) != len(candidates):
            raise ValueError("mismatched response length")
        return scores
    except Exception as e:
        emit("retrieval", {"event": "ollama_rerank_fallback", "err": str(e)})
        return heuristic_rerank(query, candidates)


def heuristic_rerank(query, candidates, must_have=None, nice_to_have=None):
    # Simple cosine + keyword overlap
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer().fit([query] + [c["section"] for c in candidates])
    qv = vec.transform([query]).toarray()[0]
    scores = []
    for c in candidates:
        cv = vec.transform([c["section"]]).toarray()[0]
        cosine = np.dot(qv, cv) / (np.linalg.norm(qv) * np.linalg.norm(cv) + 1e-8)
        overlap = 0
        if must_have:
            overlap += sum(1 for k in must_have if k in c["section"])
        if nice_to_have:
            overlap += 0.5 * sum(1 for k in nice_to_have if k in c["section"])
        scores.append(cosine + overlap)
    return scores


def rerank(query, candidates, config, must_have=None, nice_to_have=None):
    mode = config.get("reranker", "heuristic")
    if mode == "ollama":
        scores = ollama_rerank(query, candidates)
        used = "ollama"
    else:
        scores = heuristic_rerank(query, candidates, must_have, nice_to_have)
        used = "heuristic"
    return scores, used
