#!/usr/bin/env python3
"""
validate_traceability_md.py

Validate that references in the traceability matrix map to real sections
in the canonical Markdown docs (PRD, Architecture, UI Framework).

Outputs a CSV report with columns:
Feature, PRD Reference, Arch Reference, UI Reference, Status
"""

import argparse
import csv
from pathlib import Path
import re

import openpyxl


def extract_headings(md_path: Path) -> set[str]:
    """Extract section anchors (e.g., §1.2.3) from a numbered Markdown doc."""
    anchors = set()
    pattern = re.compile(r"^#+\s+(\d+(\.\d+)*)")

    with md_path.open(encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                anchors.add("§" + m.group(1))
    return anchors


def load_matrix(xlsx_path: Path, sheet_name: str = "Matrix"):
    """Load the traceability matrix rows."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb.active

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        rows.append(
            {
                "feature": row[0],
                "prd": str(row[3]) if row[3] else "",
                "arch": str(row[4]) if row[4] else "",
                "ui": str(row[5]) if row[5] else "",
            }
        )
    return rows


def validate(rows, prd_anchors, arch_anchors, ui_anchors):
    """Check each reference against the sets of known anchors."""
    results = []
    for r in rows:
        status = []
        if r["prd"] and not any(a in r["prd"] for a in prd_anchors):
            status.append("PRD MISSING")
        if r["arch"] and not any(a in r["arch"] for a in arch_anchors):
            status.append("ARCH MISSING")
        if r["ui"] and not any(a in r["ui"] for a in ui_anchors):
            status.append("UI MISSING")
        results.append(
            {
                "feature": r["feature"],
                "prd": r["prd"],
                "arch": r["arch"],
                "ui": r["ui"],
                "status": "OK" if not status else "; ".join(status),
            }
        )
    return results


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prd", required=True, help="Path to PRD Markdown")
    p.add_argument("--arch", required=True, help="Path to Architecture Markdown")
    p.add_argument("--ui", required=True, help="Path to UI Framework Markdown")
    p.add_argument("--trace", required=True, help="Path to traceability .xlsx")
    p.add_argument("--out", required=True, help="CSV output path")
    p.add_argument("--sheet", default="Matrix", help="Worksheet name (default: Matrix)")
    args = p.parse_args()

    prd_anchors = extract_headings(Path(args.prd))
    arch_anchors = extract_headings(Path(args.arch))
    ui_anchors = extract_headings(Path(args.ui))

    rows = load_matrix(Path(args.trace), args.sheet)
    results = validate(rows, prd_anchors, arch_anchors, ui_anchors)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["feature", "prd", "arch", "ui", "status"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Validation complete. Report written to {out_path}")


if __name__ == "__main__":
    main()
