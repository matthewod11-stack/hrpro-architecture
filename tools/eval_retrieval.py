import csv
from datetime import datetime
import json
from pathlib import Path

from app.retrieval.adapter import retrieve

GOLDEN_PATH = Path("evals/golden_qna.jsonl")
REPORT_PATH = Path("evals/retrieval_eval_report.csv")
MISSES_PATH = Path("evals/retrieval_eval_misses.csv")
SUMMARY_PATH = Path("evals/retrieval_eval_summary.md")
ANCHORS_PATH = Path("knowledge_base/anchors_index.csv")


# Load anchors index
anchors_map = {}
doc_map = {}
with open(ANCHORS_PATH) as f:
    next(f)
    for line in f:
        id_, anchor, doc, section, path = line.strip().split(",", 4)
        anchors_map.setdefault(anchor.strip(), []).append(
            {"id": id_, "doc": doc, "section": section, "path": path}
        )
        doc_map.setdefault(doc, []).append(anchor.strip())

# Load anchor aliases
aliases_path = Path("knowledge_base/anchor_aliases.json")
anchor_aliases = {}
if aliases_path.exists():
    with open(aliases_path) as f:
        anchor_aliases = json.load(f)


# Helper: normalize anchor
def norm_anchor(a):
    a = a.strip().replace(" ", "")
    if a.startswith("§adr-"):
        a = a.upper()
    return a


def ancestor_match(expected, returned):
    # §ADR-0001 matches §ADR-0001.1, etc.
    if expected.startswith("§ADR-") and returned.startswith(expected):
        return True
    return expected == returned


with open(GOLDEN_PATH) as f:
    goldens = [json.loads(line) for line in f if line.strip()]

rows = []
misses = []
covered = 0
miss_reasons_count = {}
for g in goldens:
    results = retrieve(g["question"], top_k=5)
    returned_anchors = [norm_anchor(r["anchor"]) for r in results]
    returned_aliases = [anchor_aliases.get(r["anchor"], []) for r in results]
    scores = [r["score"] for r in results]
    found = False
    matched = []
    for exp in g["expected_sections"]:
        exp_norm = norm_anchor(exp)
        for idx, (ret, score) in enumerate(zip(returned_anchors, scores, strict=False)):
            # ADR ancestor match
            if ancestor_match(exp_norm, ret):
                found = True
                matched.append(ret)
            # Alias match
            elif any(
                exp_norm.lower() == a.lower().replace(" ", "-")
                for a in returned_aliases[idx]
            ):
                found = True
                matched.append(ret + " (alias)")
    rows.append(
        {
            "id": g["id"],
            "question": g["question"],
            "expected_sections": ",".join(g["expected_sections"]),
            "pass": found,
            "matched_anchors": ",".join(matched),
            "notes": g.get("notes", ""),
        }
    )
    if found:
        covered += 1
    else:
        # Miss diagnostics
        miss_reason = []
        suggestions = []
        # no_adr_chunks
        adr_expected = [
            e for e in g["expected_sections"] if e.upper().startswith("§ADR-")
        ]
        for adr in adr_expected:
            if not any(norm_anchor(adr) in anchors_map for adr in adr_expected):
                miss_reason.append("no_adr_chunks")
                suggestions.append(f"expand {adr} in corpus")
        # anchor_mismatch
        for exp in g["expected_sections"]:
            exp_norm = norm_anchor(exp)
            if exp_norm not in anchors_map:
                miss_reason.append("anchor_mismatch")
                suggestions.append(f"verify anchor {exp_norm} exists in corpus")
        # retrieval_low_score
        top_score = max(scores) if scores else 0
        if top_score < 0.25:
            miss_reason.append("retrieval_low_score")
            suggestions.append("expand section text or increase top_k")
        # topic_ambiguous
        if len(set(returned_anchors)) > 3:
            miss_reason.append("topic_ambiguous")
            suggestions.append("add alias or reformulate query")
        for reason in miss_reason:
            miss_reasons_count[reason] = miss_reasons_count.get(reason, 0) + 1
        misses.append(
            {
                "id": g["id"],
                "question": g["question"],
                "expected_sections": ",".join(g["expected_sections"]),
                "returned_anchors": ",".join(returned_anchors),
                "top_score": f"{top_score:.2f}",
                "miss_reason": ";".join(miss_reason),
                "suggestions": ";".join(suggestions),
            }
        )

REPORT_PATH.parent.mkdir(exist_ok=True)
with open(REPORT_PATH, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "question",
            "expected_sections",
            "pass",
            "matched_anchors",
            "notes",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)
with open(MISSES_PATH, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "question",
            "expected_sections",
            "returned_anchors",
            "top_score",
            "miss_reason",
            "suggestions",
        ],
    )
    writer.writeheader()
    writer.writerows(misses)

coverage = covered / len(goldens)
print(f"Coverage: {covered}/{len(goldens)} ({int(coverage*100)}%)")

with open(SUMMARY_PATH, "w") as f:
    f.write("# Retrieval Eval Summary\n\n")
    f.write(f"Run: {datetime.now().isoformat()}\n\n")
    f.write(f"Coverage: {covered}/{len(goldens)} ({int(coverage*100)}%)\n\n")
    f.write("| ID | Pass | Matched Anchors |\n|---|---|---|\n")
    for r in rows:
        f.write(
            f"| {r['id']} | {'✅' if r['pass'] else '❌'} | {r['matched_anchors']} |\n"
        )
    f.write("\n## Top Miss Reasons\n")
    for reason, count in miss_reasons_count.items():
        f.write(f"- {reason}: {count}\n")
    f.write("\n## Suggested Next Fixes\n")
    all_suggestions = set()
    for m in misses:
        for s in m["suggestions"].split(";"):
            if s:
                all_suggestions.add(s)
    for s in all_suggestions:
        f.write(f"- {s}\n")
if coverage < 0.8:
    exit(1)
