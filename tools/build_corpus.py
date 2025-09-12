import sys
import re
import unicodedata
import json
from pathlib import Path
import argparse

RE_NUM = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)\s+(.*)\s*$")
RE_ADR_TOP = re.compile(r"^#{1,6}\s+ADR-(\d{4,5})[:\s-]+(.*)\s*$", re.IGNORECASE)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-adrs", action="store_true", default=True)
    parser.add_argument("--max-chars", type=int, default=2000)
    return parser.parse_args()


args = parse_args()

# --- Diagnostics and flag logging ---
print(f"FLAGS: --include-adrs={args.include_adrs} --max-chars={args.max_chars}")
external_files = list(Path("knowledge_base/sources").rglob("*.md"))
print(f"First 5 external files: {[str(f) for f in external_files[:5]]}")
external_files_count = len(external_files)


canonical_rows = 0
adr_rows = 0
external_rows = 0
external_chunks_dropped = 0
RE_H1 = re.compile(r"^\s*#\s+(.+)$")
RE_H2 = re.compile(r"^\s*##\s+(.+)$")
RE_H3 = re.compile(r"^\s*###\s+(.+)$")
RE_NUM = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)\s+(.*)$")
RE_ADR = re.compile(r"^#{1,6}\s+ADR-(\d{4,5})[:\s-]+(.*)$", re.IGNORECASE)


def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def clean_heading(text):
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_headings(text):
    headings = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for level, regex in [
            (1, RE_H1),
            (2, RE_H2),
            (3, RE_H3),
            (0, RE_NUM),
            (0, RE_ADR),
        ]:
            m = regex.match(line)
            if m:
                title = clean_heading(m.group(1) if level else m.group(2))
                headings.append((level, title, i))
    return headings


def soft_split(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    parts = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        part = text[start:end]
        if start > 0:
            part = "(cont.) " + part
        parts.append(part)
        start = end
    return parts


def first_non_empty_line(text):
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return "Untitled"


def chunks_from_external(md_path, text, split_level="h2", max_chars=2000):
    lines = text.splitlines()
    headings = []
    for i, line in enumerate(lines):
        if split_level == "h1":
            m = RE_H1.match(line)
            if m:
                headings.append((i, clean_heading(m.group(1)), 1))
        elif split_level == "h2":
            m = RE_H2.match(line)
            if m:
                headings.append((i, clean_heading(m.group(1)), 2))
        elif split_level == "h3":
            m = RE_H3.match(line)
            if m:
                headings.append((i, clean_heading(m.group(1)), 3))
    if not headings:
        # fallback: no headings, split every ~1600 chars
        text_str = "\n".join(lines)
        chunks = soft_split(text_str, max_chars)
        for idx, chunk in enumerate(chunks, 1):
            section = first_non_empty_line(text_str)
            doc_slug = slug(md_path)
            id_ = f"ext-{doc_slug}::chunk-{idx}"
            anchor = f"§ext-{doc_slug}.{idx}"
            yield {
                "id": id_,
                "doc": md_path,
                "section": section,
                "anchor": anchor,
                "path": md_path,
                "text": chunk,
                "workspace": "external",
                "priority": 0.8,
                "category": "reference",
            }
        return
    # chunk by headings
    for i, (start, title, level) in enumerate(headings):
        end = headings[i + 1][0] if i + 1 < len(headings) else len(lines)
        chunk_lines = lines[start + 1 : end]
        chunk_text = "\n".join(chunk_lines).strip()
        if not chunk_text:
            continue
        section = title or first_non_empty_line(chunk_text)
        section_slug = slug(section)
        doc_slug = slug(md_path)
        parts = soft_split(chunk_text, max_chars)
        for j, part in enumerate(parts, 1):
            suffix = f"-{chr(96+j)}" if j > 1 else ""
            id_ = f"ext-{doc_slug}::{section_slug}::{i+1}{suffix}"
            anchor = f"§ext-{section_slug}.{i+1}{suffix}"
            sec_title = section + (" (cont.)" if j > 1 else "")

            yield {
                "id": id_,
                "doc": md_path,
                "section": sec_title,
                "anchor": anchor,
                "path": md_path,
                "text": part,
                "workspace": "external",
                "priority": 0.8,
                "category": "reference",
            }


args = parse_args()

INPUTS = [
    "docs/PRD/PRD_v4.0_unified_numbered.md",
    "docs/Architecture/Architecture_v4.1_unified.md",
    "docs/UI_Framework/UIFramework_v4.0_unified_numbered.md",
]
if args.include_adrs:
    INPUTS += sorted(str(p) for p in Path("docs/adr").glob("ADR-*.md"))

corpus = []
anchors_index = []
adr_anchors = {}
row_id_set = set()


def unique_id(base):
    if base not in row_id_set:
        row_id_set.add(base)
        return base
    i = 1
    while f"{base}-{i}" in row_id_set:
        i += 1
    row_id_set.add(f"{base}-{i}")
    return f"{base}-{i}"


for path in INPUTS:
    with open(path) as f:
        lines = f.readlines()
    doc = Path(path).name
    section = None
    anchor = None
    chunk = []
    section_id = None
    current_adr = None
    adr_num = None
    # Canonical chunking (existing logic)
    for idx, line in enumerate(lines):
        m_adr = RE_ADR_TOP.match(line)
        m_num = RE_NUM.match(line)
        if m_adr:
            # Close previous ADR chunk
            if chunk and section_id:
                text = " ".join(chunk).strip()
                text = re.sub(r"```(?!json)[\s\S]*?```", "", text)
                text = re.sub(r"\s+", " ", text)
                splits = [
                    text[i : i + args.max_chars]
                    for i in range(0, len(text), args.max_chars)
                ]
                for si, split in enumerate(splits):
                    sid = section_id if si == 0 else f"{section_id}-{chr(97+si)}"
                    anch = anchor if si == 0 else f"{anchor}-{chr(97+si)}"
                    corpus.append(
                        {
                            "id": sid,
                            "doc": doc,
                            "section": section,
                            "anchor": anch,
                            "path": path,
                            "text": split,
                        }
                    )
                    anchors_index.append(
                        {
                            "id": sid,
                            "anchor": anch,
                            "doc": doc,
                            "section": section,
                            "path": path,
                        }
                    )
            adr_num = m_adr.group(1).upper()
            current_adr = f"ADR-{adr_num}"
            section_id = unique_id(current_adr)
            anchor = f"§{current_adr}"
            section = f"{current_adr}: {m_adr.group(2).strip()}"
            chunk = []
            adr_anchors.setdefault(doc, []).append(anchor)
            adr_rows += 1
        elif current_adr and m_num:
            # Numbered heading inside ADR
            if chunk and section_id:
                text = " ".join(chunk).strip()
                text = re.sub(r"```(?!json)[\s\S]*?```", "", text)
                text = re.sub(r"\s+", " ", text)
                splits = [
                    text[i : i + args.max_chars]
                    for i in range(0, len(text), args.max_chars)
                ]
                for si, split in enumerate(splits):
                    sid = section_id if si == 0 else f"{section_id}-{chr(97+si)}"
                    anch = anchor if si == 0 else f"{anchor}-{chr(97+si)}"
                    corpus.append(
                        {
                            "id": sid,
                            "doc": doc,
                            "section": section,
                            "anchor": anch,
                            "path": path,
                            "text": split,
                        }
                    )
                    anchors_index.append(
                        {
                            "id": sid,
                            "anchor": anch,
                            "doc": doc,
                            "section": section,
                            "path": path,
                        }
                    )
            num, title = m_num.groups()
            section_id = unique_id(f"{current_adr}.{num}")
            anchor = f"§{current_adr}.{num}"
            section = f"{current_adr} — {num} {title.strip()}"
            chunk = []
            adr_anchors.setdefault(doc, []).append(anchor)
            adr_rows += 1
        elif m_num and not current_adr:
            # Numbered heading outside ADR
            if chunk and section_id:
                text = " ".join(chunk).strip()
                text = re.sub(r"```(?!json)[\s\S]*?```", "", text)
                text = re.sub(r"\s+", " ", text)
                splits = [
                    text[i : i + args.max_chars]
                    for i in range(0, len(text), args.max_chars)
                ]
                for si, split in enumerate(splits):
                    sid = section_id if si == 0 else f"{section_id}-{chr(97+si)}"
                    anch = anchor if si == 0 else f"{anchor}-{chr(97+si)}"
                    corpus.append(
                        {
                            "id": sid,
                            "doc": doc,
                            "section": section,
                            "anchor": anch,
                            "path": path,
                            "text": split,
                        }
                    )
                    anchors_index.append(
                        {
                            "id": sid,
                            "anchor": anch,
                            "doc": doc,
                            "section": section,
                            "path": path,
                        }
                    )
            num, title = m_num.groups()
            section_id = unique_id(f"{doc.split('_')[0].lower()}-{num}")
            anchor = f"§{num}"
            section = f"{num} {title.strip()}"
            chunk = []
            canonical_rows += 1
        else:
            chunk.append(line.strip())
    # last chunk
    if chunk and section_id:
        text = " ".join(chunk).strip()
        text = re.sub(r"```(?!json)[\s\S]*?```", "", text)
        text = re.sub(r"\s+", " ", text)
        splits = [
            text[i : i + args.max_chars] for i in range(0, len(text), args.max_chars)
        ]
        for si, split in enumerate(splits):
            sid = section_id if si == 0 else f"{section_id}-{chr(97+si)}"
            anch = anchor if si == 0 else f"{anchor}-{chr(97+si)}"
            corpus.append(
                {
                    "id": sid,
                    "doc": doc,
                    "section": section,
                    "anchor": anch,
                    "path": path,
                    "text": split,
                }
            )
            anchors_index.append(
                {
                    "id": sid,
                    "anchor": anch,
                    "doc": doc,
                    "section": section,
                    "path": path,
                }
            )
            canonical_rows += 1

# External Markdown chunking

# Load anchor aliases

aliases_path = Path("knowledge_base/anchor_aliases.json")
anchor_aliases = {}
if aliases_path.exists():
    with open(aliases_path) as f:
        anchor_aliases = json.load(f)

external_dir = Path("knowledge_base/sources")
if external_dir.exists():
    for ext_path in external_dir.rglob("*.md"):
        with open(ext_path) as f:
            text = f.read()
        ext_chunks = list(
            chunks_from_external(
                str(ext_path.relative_to(".")),
                text,
                split_level="h2",
                max_chars=args.max_chars,
            )
        )
        for row in ext_chunks:
            # Diagnostics/assertions for external
            if not row.get("id") or not row.get("anchor") or not row.get("section"):
                print(f"ERROR: External chunk missing id/anchor/section: {row}")
                external_chunks_dropped += 1
                continue
            if not row["anchor"].startswith("§ext-"):
                print(f"ERROR: External anchor not §ext-: {row['anchor']}")
                external_chunks_dropped += 1
                continue
            if row["workspace"] != "external":
                print(f"ERROR: External chunk workspace not 'external': {row}")
                external_chunks_dropped += 1
                continue
            # Add anchor_aliases if present
            row["anchor_aliases"] = anchor_aliases.get(row["anchor"], [])
            corpus.append(row)
            anchors_index.append(
                {
                    "id": row["id"],
                    "anchor": row["anchor"],
                    "doc": row["doc"],
                    "section": row["section"],
                    "path": row["path"],
                }
            )
            external_rows += 1

# --- Final diagnostics ---
print(
    f"canonical_rows={canonical_rows} adr_rows={adr_rows} external_rows={external_rows}"
)
if external_files_count > 0 and external_rows == 0:
    print(
        "External sources detected but produced zero chunks—check split logic & sanitize/dedupe thresholds."
    )
    sys.exit(2)


# Write corpus
out_path = Path("knowledge_base/corpus.jsonl")
out_path.parent.mkdir(exist_ok=True)
with open(out_path, "w") as f:
    for row in corpus:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

# Write anchors index
anchors_path = Path("knowledge_base/anchors_index.csv")
with open(anchors_path, "w") as f:
    f.write("id,anchor,doc,section,path\n")
    for row in anchors_index:
        f.write(
            f"{row['id']},{row['anchor']},{row['doc']},{row['section']},{row['path']}\n"
        )

# Diagnostics report
report_path = Path("knowledge_base/build_report.md")
with open(report_path, "w") as f:
    f.write("# Corpus Build Report\n\n")
    f.write(f"Docs parsed: {len(INPUTS)}\n")
    f.write(f"Rows written: {len(corpus)}\n\n")
    f.write(f"External files seen: {external_files_count}\n")
    f.write(f"External chunks written: {external_rows}\n")
    f.write(f"External chunks dropped (sanitize/dedupe): {external_chunks_dropped}\n")
    for p in INPUTS:
        rows = [r for r in corpus if r["path"] == p]
        if not rows:
            continue
        avg_len = int(sum(len(r["text"]) for r in rows) / len(rows))
        max_len = max(len(r["text"]) for r in rows)
        f.write(
            f"**{Path(p).name}**: {len(rows)} rows, avg_len={avg_len}, max_len={max_len}\n"
        )
        if "ADR-" in Path(p).name:
            anchors = [r["anchor"] for r in rows][:10]
            f.write(f"  First 10 anchors: {', '.join(anchors)}\n")
