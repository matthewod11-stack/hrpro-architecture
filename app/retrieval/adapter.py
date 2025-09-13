import json
from pathlib import Path
import string
import time

import joblib
import numpy as np
from scipy import sparse
import yaml

from app.retrieval.query_rewrite import rewrite
from app.retrieval.rerank import rerank

INDEX_DIR = Path(__file__).parent.parent.parent / "versions/index"
CORPUS_PATH = Path(__file__).parent.parent.parent / "knowledge_base/corpus.jsonl"
META_PATH = INDEX_DIR / "meta.json"
MATRIX_PATH = INDEX_DIR / "matrix.npz"
VEC_PATH = INDEX_DIR / "tfidf.joblib"
NN_PATH = INDEX_DIR / "nn.joblib"
TELEMETRY_PATH = Path(__file__).parent.parent.parent / "logs/dev_telemetry.jsonl"

_vectorizer = _matrix = _nn = _meta = None


def _load():
    global _vectorizer, _matrix, _nn, _meta
    if _vectorizer is None:
        _vectorizer = joblib.load(VEC_PATH)
    if _matrix is None:
        _matrix = sparse.load_npz(MATRIX_PATH)
    if _nn is None:
        _nn = joblib.load(NN_PATH)
    if _meta is None:
        with open(META_PATH) as f:
            _meta = json.load(f)


def _expand_synonyms(query):
    syn_path = Path(__file__).parent.parent.parent / "knowledge_base/synonyms.json"
    if not syn_path.exists():
        return [query]
    with open(syn_path) as f:
        syns = json.load(f)
    tokens = set(
        query.lower().translate(str.maketrans("", "", string.punctuation)).split()
    )
    expanded = set([query])
    for k, v in syns.items():
        if k in query.lower():
            expanded.update(v)
        for t in tokens:
            if t in k:
                expanded.update(v)
    return list(expanded)[:6]


def retrieve(topic: str, top_k: int = 5):
    """
    Returns up to top_k snippets sorted by hybrid + reranker similarity.
    Each snippet:
    {
      "id": str, "doc": str, "section": str, "anchor": str,
      "path": str, "dense": float, "sparse": float, "title_bonus": float, "score": float, "snippet": str
    }
    """
    _load()
    t0 = time.time()
    # Load config
    with open(Path(__file__).parent.parent.parent / "config/retrieval.yaml") as f:
        config = yaml.safe_load(f)
    # Query rewrite
    aliases_path = (
        Path(__file__).parent.parent.parent / "knowledge_base/anchor_aliases.json"
    )
    anchor_aliases = {}
    if aliases_path.exists():
        with open(aliases_path) as f:
            anchor_aliases = json.load(f)
    if config.get("query_rewrite", True):
        rewrite_out = rewrite(topic, anchor_aliases)
        expanded_query = rewrite_out.get("expanded_query", topic)
        # All imports are at the top of the file
        must_have = []
        nice_to_have = []
    else:
        expanded_query = topic
        must_have = []
        nice_to_have = []
    # Synonym expansion
    queries = _expand_synonyms(expanded_query)
    queries = [
        q.lower().translate(str.maketrans("", "", string.punctuation)).strip()
        for q in queries
    ]
    # FAISS dense retrieval (top rerank_candidates)
    qv = _vectorizer.transform([expanded_query])
    n_candidates = int(config.get("index", {}).get("rerank_candidates", 40))
    dists, idxs = _nn.kneighbors(qv, n_neighbors=n_candidates)
    with open(CORPUS_PATH) as f:
        lines = f.readlines()
    candidates = []
    for rank, (i, dist) in enumerate(zip(idxs[0], dists[0], strict=False)):
        meta = _meta[str(i)]
        text = json.loads(lines[i])["text"]
        tfidf_vec = _vectorizer.transform([text])
        sparse_score = float(np.dot(qv.toarray(), tfidf_vec.toarray().T)[0][0])
        section = meta.get("section", "").lower()
        title_bonus = 0.0
        for q in queries:
            if any(t in section for t in q.split()):
                title_bonus = 0.1
                break
        dense_score = float(1 - dist)
        hybrid_score = 0.65 * dense_score + 0.35 * sparse_score + title_bonus
        candidates.append(
            {
                **meta,
                "dense": dense_score,
                "sparse": sparse_score,
                "title_bonus": title_bonus,
                "hybrid_score": hybrid_score,
                "snippet": text[:600],
            }
        )
    # Rerank
    rerank_scores, rerank_used = rerank(
        expanded_query, candidates, config, must_have, nice_to_have
    )
    final_results = []
    for c, rscore in zip(candidates, rerank_scores, strict=False):
        final_score = 0.6 * c["hybrid_score"] + 0.4 * rscore
        c["rerank_score"] = rscore
        c["score"] = final_score
        final_results.append(c)
    final_results.sort(key=lambda r: r["score"], reverse=True)
    top_k_val = int(config.get("index", {}).get("top_k", top_k))
    elapsed = int((time.time() - t0) * 1000)
    with open(TELEMETRY_PATH, "a") as f:
        f.write(
            json.dumps({"event": "rerank", "used": rerank_used, "ms": elapsed}) + "\n"
        )
    return final_results[:top_k_val]
