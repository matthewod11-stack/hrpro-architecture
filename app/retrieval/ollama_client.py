import os
import json
import time
from pathlib import Path
import requests
import hashlib
import sqlite3
import numpy as np
from datetime import datetime


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_TIMEOUT_S = int(os.getenv("OLLAMA_TIMEOUT_S", "8"))
OLLAMA_MODEL_REWRITE = os.getenv("OLLAMA_MODEL_REWRITE", "llama3.1:8b")
OLLAMA_MODEL_GENERAL = os.getenv("OLLAMA_MODEL_GENERAL", "llama3.1:8b")
LOG_PATH = Path("logs/dev_telemetry.jsonl")


def _trunc(s: str, n: int = 200) -> str:
    s = s or ""
    return (s[:n] + "…") if len(s) > n else s


def _log_event(event: str, **kwargs):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"event": event, **kwargs, "ts": int(time.time() * 1000)}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def chat(
    model: str, messages: list[dict], stream: bool = False, options: dict | None = None
) -> dict:
    # requests imported at top

    url = f"{OLLAMA_URL}/api/chat"
    payload = {"model": model, "messages": messages, "stream": stream}
    if options:
        payload["options"] = options
    try:
        r = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT_S)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        _log_event(
            "ollama_http_error",
            endpoint="/api/chat",
            status=None,
            model=model,
            trunc_payload=_trunc(json.dumps(payload, ensure_ascii=False)),
            err=str(e),
        )
        raise


def generate(
    model: str, prompt: str, stream: bool = False, options: dict | None = None
) -> dict:
    # requests imported at top

    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": stream}
    if options:
        payload["options"] = options
    try:
        r = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT_S)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        _log_event(
            "ollama_http_error",
            endpoint="/api/generate",
            status=None,
            model=model,
            trunc_payload=_trunc(prompt),
            err=str(e),
        )
        raise


def health_ok() -> bool:
    # requests imported at top

    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.ok
    except Exception:
        return False


## (imports already at top)

CACHE_PATH = os.path.join(
    os.path.dirname(__file__), "../../versions/cache/embeddings.sqlite"
)
BATCH_SIZE = 64
TIMEOUT = 30
MAX_RETRIES = 3


def _mk_key(model: str, text: str) -> str:
    return hashlib.sha256(f"{model}\n{text}".encode()).hexdigest()


def _to_blob(vec: np.ndarray) -> bytes:
    arr = np.ascontiguousarray(vec.astype(np.float32, copy=False))
    return arr.tobytes(order="C")


def _from_blob(blob: bytes, dim: int) -> np.ndarray:
    arr = np.frombuffer(blob, dtype=np.float32, count=dim)
    assert arr.shape == (
        dim,
    ), f"Blob shape mismatch: got {arr.shape}, expected ({dim},)"
    return arr


def _ensure_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            key TEXT PRIMARY KEY,
            model TEXT NOT NULL,
            dim INTEGER NOT NULL,
            bytes BLOB NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model)")


def cache_get_many(model: str, texts: list[str]) -> dict[int, np.ndarray]:
    conn = sqlite3.connect(CACHE_PATH)
    _ensure_schema(conn)
    keys = [_mk_key(model, t) for t in texts]
    qmarks = ",".join(["?"] * len(keys))
    cur = conn.execute(
        f"SELECT key, dim, bytes FROM embeddings WHERE key IN ({qmarks}) AND model=?",
        (*keys, model),
    )
    out = {}
    key_to_idx = {k: i for i, k in enumerate(keys)}
    for row in cur.fetchall():
        k, dim, blob = row
        idx = key_to_idx[k]
        out[idx] = _from_blob(blob, dim)
    conn.close()
    return out


def cache_put_many(model: str, texts: list[str], vectors: list[np.ndarray]) -> None:
    assert len(texts) == len(vectors), "Texts and vectors must match in length"
    dim = vectors[0].shape[0]
    for v in vectors:
        assert v.shape == (dim,), f"All vectors must have shape ({dim},)"
        assert v.dtype == np.float32, "All vectors must be float32"
    conn = sqlite3.connect(CACHE_PATH)
    _ensure_schema(conn)
    now = datetime.utcnow().isoformat()
    rows = [
        (_mk_key(model, t), model, dim, _to_blob(v), now)
        for t, v in zip(texts, vectors)
    ]
    conn.execute("BEGIN IMMEDIATE")
    conn.executemany(
        "INSERT OR IGNORE INTO embeddings (key, model, dim, bytes, created_at) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def embed_texts(texts: list[str], model=None, endpoint=None) -> np.ndarray:
    # Read config
    import yaml

    cfg_path = os.path.join(os.path.dirname(__file__), "../../config/retrieval.yaml")
    if model is None or endpoint is None:
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        model = model or cfg.get("ollama", {}).get("model", "mxbai-embed-large")
        endpoint = endpoint or cfg.get("ollama", {}).get(
            "endpoint", "http://localhost:11434"
        )
    N = len(texts)
    # Batch get from cache
    hits = cache_get_many(model, texts)
    out = [None] * N
    for idx, vec in hits.items():
        out[idx] = vec
    misses = [(i, texts[i]) for i in range(N) if out[i] is None]
    if misses:
        for start in range(0, len(misses), BATCH_SIZE):
            batch = misses[start : start + BATCH_SIZE]
            batch_idx, batch_texts = zip(*batch)
            for attempt in range(MAX_RETRIES):
                try:
                    resp = requests.post(
                        f"{endpoint}/api/embeddings",
                        json={"model": model, "input": list(batch_texts)},
                        timeout=TIMEOUT,
                    )
                    resp.raise_for_status()
                    embeds = resp.json()["embeddings"]
                    assert len(embeds) == len(
                        batch_texts
                    ), f"Ollama returned {len(embeds)} for {len(batch_texts)}"
                    dim = len(embeds[0])
                    batch_vecs = [
                        np.ascontiguousarray(np.array(e, dtype=np.float32))
                        for e in embeds
                    ]
                    for v in batch_vecs:
                        assert v.shape == (
                            dim,
                        ), f"Vector shape mismatch: {v.shape} vs {dim}"
                        if np.isnan(v).any():
                            raise ValueError(
                                f"NaN in embedding for batch idx {batch_idx}"
                            )
                    cache_put_many(model, list(batch_texts), batch_vecs)
                    for i, v in zip(batch_idx, batch_vecs):
                        out[i] = v
                    break
                except Exception:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    time.sleep(0.25 * (2**attempt))
    # Final checks
    arr = np.stack(out)
    assert arr.ndim == 2, f"Returned array shape {arr.shape}"
    assert arr.dtype == np.float32, f"Returned dtype {arr.dtype}"
    return arr


# --- CLI entrypoint ---
if __name__ == "__main__":
    import sys

    texts = sys.argv[1:]
    arr = embed_texts(texts)
    print(f"Embedding dim: {arr.shape[1]}")
    hits = cache_get_many("mxbai-embed-large", texts)
    for i, t in enumerate(texts):
        print(f"Text {i}: {'HIT' if i in hits else 'MISS'}")
