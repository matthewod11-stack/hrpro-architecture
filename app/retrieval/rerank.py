import requests
import yaml
import numpy as np


def ollama_rerank(query, candidates):
    with open("config/retrieval.yaml") as f:
        cfg = yaml.safe_load(f)
    endpoint = cfg.get("ollama", {}).get("endpoint", "http://localhost:11434")
    model = cfg.get("ollama", {}).get("model", "phi3:latest")
    scores = []
    for c in candidates:
        prompt = f"""
Given the query and candidate passage, score relevance 0-1 based on keyword coverage and HR/internal spec fit.
Query: {query}
Passage: {c['section']}\n{c['snippet'][:400]}
Respond with a float score only.
"""
        resp = requests.post(
            f"{endpoint}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        score = float(resp.json()["response"].strip())
        scores.append(score)
    return scores


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
