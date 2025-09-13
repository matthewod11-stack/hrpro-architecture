#!/usr/bin/env python3
"""Auto-diagnose and patch legacy rows in the traceability matrix.

The script uses fuzzy matching against the PRD, Architecture and UI spec
Markdown files to fill in missing or incorrect references. Only legacy rows are
modified – rows whose ID starts with ``PR-2`` are left untouched for safety.
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from traceability_utils import (
    discover_spec_files,
    load_md_sections,
    parse_ref_number,
)

# ---------------------------------------------------------------------------
# Fuzzy matching helpers
# ---------------------------------------------------------------------------

def best_section_match(text: str, titles: Dict[str, str], cutoff: float = 0.6) -> Tuple[str, str] | None:
    """Return ``(section, title)`` for the best fuzzy match against ``text``."""
    if not isinstance(text, str) or not text.strip():
        return None
    candidates = difflib.get_close_matches(text, titles.values(), n=1, cutoff=cutoff)
    if not candidates:
        return None
    title = candidates[0]
    # Reverse lookup section number
    for sec, t in titles.items():
        if t == title:
            return sec, t
    return None


def format_ref(prefix: str, md_path: Path, section: str, title: str) -> str:
    """Format a traceability reference string."""
    rel = md_path.relative_to(Path(".").resolve())
    # Extract version from filename if possible
    version = ""
    m = re.search(r"v(\d+(?:\.\d+)*)", md_path.name, re.IGNORECASE)
    if m:
        version = f" v{m.group(1)}"
    return f"{prefix}{version} §{section} ({title}) ({rel})"


# ---------------------------------------------------------------------------
# Main patching routine
# ---------------------------------------------------------------------------

def main() -> None:
    repo_root = Path(".").resolve()
    specs = discover_spec_files(repo_root)
    prd_md, arch_md, ui_md = specs["prd"], specs["arch"], specs["ui"]

    trace_xlsx = repo_root / "docs/traceability/Traceability_v4.1_prefilled.xlsx"
    out_xlsx = trace_xlsx.with_name(trace_xlsx.stem + "_auto_patched.xlsx")

    print(f"[INFO] Traceability input: {trace_xlsx}")
    print(f"[INFO] Output will be:   {out_xlsx}")

    # Load spec sections
    prd_sections, prd_titles = load_md_sections(prd_md)
    arch_sections, arch_titles = load_md_sections(arch_md)
    ui_sections, ui_titles = load_md_sections(ui_md)

    # Load matrix
    df = pd.read_excel(trace_xlsx)
    col_flow = "UI Element / Flow"
    col_prd = next((c for c in df.columns if str(c).strip().lower().startswith("prd")), "PRD Requirement (short)")
    col_arch = next((c for c in df.columns if "arch" in str(c).strip().lower()), "Architecture Mapping")
    col_ui = next((c for c in df.columns if str(c).strip().lower().startswith("ui")), None)

    patched_rows = []

    for idx, row in df.iterrows():
        rid = str(row.get("ID", ""))
        if rid.startswith("PR-2"):
            continue  # never touch PR-2 rows

        flow = str(row.get(col_flow, ""))

        # PRD --------------------------------------------------------------
        prd_ref = str(row.get(col_prd, "") or "")
        prd_num = parse_ref_number(prd_ref)
        if not prd_num or prd_num not in prd_sections:
            match = best_section_match(flow, prd_titles)
            if match:
                sec, title = match
                df.at[idx, col_prd] = format_ref("PRD", prd_md, sec, title)
                patched_rows.append((rid, "PRD", sec))

        # Architecture ----------------------------------------------------
        arch_ref = str(row.get(col_arch, "") or "")
        arch_num = parse_ref_number(arch_ref)
        if not arch_num or arch_num not in arch_sections:
            match = best_section_match(flow, arch_titles)
            if match:
                sec, title = match
                df.at[idx, col_arch] = format_ref("Arch", arch_md, sec, title)
                patched_rows.append((rid, "ARCH", sec))

        # UI spec ---------------------------------------------------------
        if col_ui and ui_md:
            ui_ref = str(row.get(col_ui, "") or "")
            ui_num = parse_ref_number(ui_ref)
            if not ui_num or ui_num not in ui_sections:
                match = best_section_match(flow, ui_titles)
                if match:
                    sec, title = match
                    df.at[idx, col_ui] = format_ref("UI", ui_md, sec, title)
                    patched_rows.append((rid, "UI", sec))

    df.to_excel(out_xlsx, index=False)
    print(f"[DONE] Patched {len(patched_rows)} references -> {out_xlsx}")


if __name__ == "__main__":
    main()
