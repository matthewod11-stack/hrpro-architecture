#!/usr/bin/env python3
"""
validate_traceability_md.py

Validate that references in the traceability matrix map to real sections
in the canonical Markdown docs (PRD, Architecture, UI Framework).

- Extracts anchors from numbered Markdown headings:
    "# 1", "## 1.2", "### 1.2.3" -> "§1", "§1.2", "§1.2.3"
- Reads an Excel matrix (default sheet "Matrix") and looks for columns:
    "Feature Name", "PRD Reference", "Arch Reference", "UI Reference"
  Header names are matched case-insensitively and loosely. If headers
  are missing, it falls back to indices [0, 3, 4, 5].
- For each row, checks if any "§X(.Y)*" token in the reference cell
  is present in the extracted anchor set from the corresponding doc.

Outputs CSV with columns:
    feature, prd, arch, ui, status

Exit code:
    0 -> All rows OK
    1 -> Any row has a missing reference
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import csv
from dataclasses import dataclass
from pathlib import Path
import re
import sys

import openpyxl

# Matches numbered headings like: "# 1", "## 1.2", "### 1.2.3 Title"
ANCHOR_RE = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)\b")

# Extract tokens like "§1", "§1.2", "§12.3.4" from a freeform cell
SECTION_TOKEN_RE = re.compile(r"§\d+(?:\.\d+)*")


@dataclass
class MatrixRow:
    feature: str
    prd: str
    arch: str
    ui: str


def _to_str(x: object) -> str:
    return ("" if x is None else str(x)).strip()


def extract_anchors(md_path: Path) -> set[str]:
    """Extract section anchors (e.g., '§1.2.3') from a numbered Markdown doc."""
    anchors: set[str] = set()
    with md_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            m = ANCHOR_RE.match(line)
            if m:
                anchors.add("§" + m.group(1))
    return anchors


def _safe_sheet(wb, name: str):
    """Return the named sheet if present; else the first sheet."""
    return wb[name] if name in wb.sheetnames else wb[wb.sheetnames[0]]


def _header_index_map(headers: Sequence[str]) -> dict[str, int]:
    """
    Build a case/format-insensitive index map for common columns.
    Accept many variants to be resilient to header changes.
    """
    norm = [h.strip().lower().replace("_", " ") for h in headers]

    def find_one(cands: Sequence[str]) -> int | None:
        for i, h in enumerate(norm):
            for c in cands:
                if c in h:
                    return i
        return None

    idx_feature = find_one(["feature name", "feature", "name"])
    idx_prd = find_one(["prd reference", "prd", "product requirements"])
    idx_arch = find_one(["arch reference", "architecture mapping", "arch"])
    idx_ui = find_one(["ui reference", "ui framework", "ui"])

    return {
        "feature": -1 if idx_feature is None else idx_feature,
        "prd": -1 if idx_prd is None else idx_prd,
        "arch": -1 if idx_arch is None else idx_arch,
        "ui": -1 if idx_ui is None else idx_ui,
    }


def _fallback_indices() -> dict[str, int]:
    """
    Fallback to legacy positional layout:
      0: Feature Name
      3: PRD Reference
      4: Arch Reference
      5: UI Reference
    """
    return {"feature": 0, "prd": 3, "arch": 4, "ui": 5}


def load_matrix(xlsx_path: Path, sheet_name: str = "Matrix") -> list[MatrixRow]:
    """
    Load rows from the matrix spreadsheet. Tries header-based mapping first,
    then falls back to positional indices if headers are missing/unknown.
    """
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = _safe_sheet(wb, sheet_name)

    rows: list[MatrixRow] = []

    # Read headers in the first row (if present)
    header_row = None
    for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
        header_row = ["" if x is None else str(x) for x in row]
        break

    if header_row:
        idx_map = _header_index_map(header_row)
    else:
        idx_map = _fallback_indices()

    # If headers weren't helpful, fall back
    if any(idx_map[k] < 0 for k in ("feature", "prd", "arch", "ui")):
        idx_map = _fallback_indices()

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not any(row):
            continue

        feature = (
            _to_str(row[idx_map["feature"]]) if len(row) > idx_map["feature"] else ""
        )
        prd = _to_str(row[idx_map["prd"]]) if len(row) > idx_map["prd"] else ""
        arch = _to_str(row[idx_map["arch"]]) if len(row) > idx_map["arch"] else ""
        ui = _to_str(row[idx_map["ui"]]) if len(row) > idx_map["ui"] else ""

        rows.append(MatrixRow(feature=feature, prd=prd, arch=arch, ui=ui))

    return rows


def _tokens_in(blob: str) -> set[str]:
    """Return all unique '§X(.Y)*' tokens present in the string."""
    return set(SECTION_TOKEN_RE.findall(blob))


def validate(
    rows: list[MatrixRow],
    prd_anchors: set[str],
    arch_anchors: set[str],
    ui_anchors: set[str],
) -> list[dict[str, str]]:
    """
    Validate each row by checking whether any §-token in each reference cell
    is present in the corresponding document's anchor set.
    """
    results: list[dict[str, str]] = []
    for r in rows:
        issues: list[str] = []

        prd_tokens = _tokens_in(r.prd)
        arch_tokens = _tokens_in(r.arch)
        ui_tokens = _tokens_in(r.ui)

        if r.prd and not any(t in prd_anchors for t in prd_tokens):
            issues.append("PRD MISSING")
        if r.arch and not any(t in arch_anchors for t in arch_tokens):
            issues.append("ARCH MISSING")
        if r.ui and not any(t in ui_anchors for t in ui_tokens):
            issues.append("UI MISSING")

        results.append(
            {
                "feature": r.feature,
                "prd": r.prd,
                "arch": r.arch,
                "ui": r.ui,
                "status": "OK" if not issues else "; ".join(issues),
            }
        )

    return results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--prd", required=True, help="Path to PRD Markdown")
    p.add_argument("--arch", required=True, help="Path to Architecture Markdown")
    p.add_argument("--ui", required=True, help="Path to UI Framework Markdown")
    p.add_argument("--trace", required=True, help="Path to traceability .xlsx")
    p.add_argument("--out", required=True, help="CSV output path")
    p.add_argument(
        "--sheet",
        default="Matrix",
        help='Worksheet name (default: "Matrix")',
    )
    args = p.parse_args()

    prd_path = Path(args.prd)
    arch_path = Path(args.arch)
    ui_path = Path(args.ui)
    trace_path = Path(args.trace)
    out_path = Path(args.out)

    prd_anchors = extract_anchors(prd_path)
    arch_anchors = extract_anchors(arch_path)
    ui_anchors = extract_anchors(ui_path)

    rows = load_matrix(trace_path, args.sheet)
    results = validate(rows, prd_anchors, arch_anchors, ui_anchors)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["feature", "prd", "arch", "ui", "status"]
        )
        writer.writeheader()
        writer.writerows(results)

    total = len(results)
    bad = sum(1 for r in results if r["status"] != "OK")
    ok = total - bad
    print(
        f"Validation complete. OK={ok} / TOTAL={total}. "
        f"Report written to {out_path}"
    )

    # Exit non-zero if any row is not OK (so CI fails)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
