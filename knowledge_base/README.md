# Knowledge Base Format

- `corpus.jsonl`: Each line is a JSON object with id, doc, section, anchor, path, text (≤2000 chars).
- Split on numbered headings; keep anchors (e.g., §2.1).
- Strip code except json blocks.
- Collapse whitespace, keep bullets.
- Truncate text at 2000 chars.

Artifacts:
- `versions/index/`: TF-IDF vectorizer, matrix, NearestNeighbors, meta.json

To build:

    make kb-build
    make kb-index
    make kb-retrieve

See also: `app/retrieval/adapter.py` for the retrieval interface.

# External KB Sync
- Configure sources in `external_kb.yaml`.
- Run `make kb-reindex` to clone/convert/inject anchors and rebuild indexes.
- External anchors use `§ext-<id>` prefix. Example: `<!-- §ext-foundryhr.file-slug -->`.
