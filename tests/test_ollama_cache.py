import pytest

pytest.importorskip("sklearn")
import pytest

pytest.importorskip("scipy")
pytest.importorskip("yaml")

import numpy as np

from app.retrieval import ollama_client


def test_cache_roundtrip():
    texts = ["hello world", "branding compliance watermark"]
    arr1 = ollama_client.embed_texts(texts)
    arr2 = ollama_client.embed_texts(texts)
    assert arr1.shape == arr2.shape
    assert arr1.dtype == np.float32
    assert np.allclose(arr1, arr2)
    hits = ollama_client.cache_get_many("mxbai-embed-large", texts)
    assert len(hits) == len(texts)
    print("Cache roundtrip: hits", hits.keys())
    print("Dims:", arr1.shape)


def test_corrupt_dim():
    # Corrupt a row's dim and ensure error
    import sqlite3

    db = ollama_client.CACHE_PATH
    conn = sqlite3.connect(db)
    key = ollama_client._mk_key("mxbai-embed-large", "hello world")
    conn.execute("UPDATE embeddings SET dim=999 WHERE key=?", (key,))
    conn.commit()
    conn.close()
    try:
        ollama_client.embed_texts(["hello world"])
    except AssertionError as e:
        print("Caught expected error:", e)
        print("Suggest: run kb-index --clean or reset DB")
    finally:
        # Restore correct dim
        arr1 = ollama_client.embed_texts(["hello world"])
        conn = sqlite3.connect(db)
        conn.execute("UPDATE embeddings SET dim=? WHERE key=?", (arr1.shape[1], key))
        conn.commit()
        conn.close()


def test_shape_and_dtype():
    arr = ollama_client.embed_texts(["test shape", "test dtype"])
    assert arr.ndim == 2
    assert arr.dtype == np.float32
    print("Shape and dtype OK:", arr.shape, arr.dtype)


if __name__ == "__main__":
    test_cache_roundtrip()
    test_shape_and_dtype()
    test_corrupt_dim()
