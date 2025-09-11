import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy import sparse
from datetime import datetime

CORPUS_PATH = Path("knowledge_base/corpus.jsonl")
INDEX_DIR = Path("versions/index/")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

rows = [json.loads(line) for line in open(CORPUS_PATH)]
texts = [r["text"] for r in rows]

vectorizer = TfidfVectorizer(
    analyzer="word", ngram_range=(1, 2), lowercase=True, min_df=1
)
X = vectorizer.fit_transform(texts)

nn = NearestNeighbors(metric="cosine")
nn.fit(X)

joblib.dump(vectorizer, INDEX_DIR / "tfidf.joblib")
sparse.save_npz(INDEX_DIR / "matrix.npz", X)
joblib.dump(nn, INDEX_DIR / "nn.joblib")

meta = {
    str(i): {k: r[k] for k in ("id", "doc", "section", "anchor", "path")}
    for i, r in enumerate(rows)
}
meta["created_at"] = datetime.now().isoformat()
with open(INDEX_DIR / "meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"Indexed {len(rows)} sections. Artifacts in {INDEX_DIR}")
