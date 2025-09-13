#!/usr/bin/env python3
"""Traceability validator with spec autodiscovery."""

import sys
from pathlib import Path

import pandas as pd

from traceability_utils import (
    discover_spec_files,
    load_md_sections,
    parse_ref_number,
)

def main():
    repo_root = Path(".").resolve()

    # Defaults (paths can be overridden via CLI flags). Autodiscover spec files
    specs = discover_spec_files(repo_root)
    prd_md = specs["prd"] or repo_root / "docs/PRD/PRD_v4.0_unified_numbered.md"
    arch_md = specs["arch"] or repo_root / "docs/Architecture/Architecture_v4.1.md"
    ui_md = specs["ui"] or repo_root / "docs/UI_Framework/UIFramework_v4.0_unified_numbered.md"

    trace_xlsx = repo_root / "docs/traceability/Traceability_v4.1_completed_with_notes.xlsx"
    out_csv = repo_root / "docs/traceability/Traceability_link_check.csv"

    for arg in sys.argv[1:]:
        if arg.startswith("--prd="):   prd_md  = Path(arg.split("=",1)[1]).resolve()
        elif arg.startswith("--arch="): arch_md = Path(arg.split("=",1)[1]).resolve()
        elif arg.startswith("--ui="):   ui_md   = Path(arg.split("=",1)[1]).resolve()
        elif arg.startswith("--trace="):trace_xlsx = Path(arg.split("=",1)[1]).resolve()
        elif arg.startswith("--out="):  out_csv    = Path(arg.split("=",1)[1]).resolve()

    print(f"[INFO] PRD (md):  {prd_md}")
    print(f"[INFO] Arch (md): {arch_md}")
    print(f"[INFO] UI  (md):  {ui_md if ui_md.exists() else '(missing or skipped)'}")
    print(f"[INFO] Traceability: {trace_xlsx}")

    prd_sections,  prd_titles  = load_md_sections(prd_md)
    arch_sections, arch_titles = load_md_sections(arch_md)
    ui_sections,   ui_titles   = load_md_sections(ui_md) if ui_md.exists() else (set(), {})

    # Load matrix
    df = pd.read_excel(trace_xlsx)

    # Column names (robust to slight variations)
    col_flow = "UI Element / Flow"
    col_prd  = next((c for c in df.columns if str(c).strip().lower().startswith("prd")), "PRD Requirement (short)")
    col_arch = next((c for c in df.columns if "arch" in str(c).strip().lower()), "Architecture Mapping")
    col_ui   = next((c for c in df.columns if str(c).strip().lower().startswith("ui")), None)  # optional

    rows = []
    for _, row in df.iterrows():
        rid   = row.get("ID", "")
        flow  = row.get(col_flow, "")

        prd_ref  = str(row.get(col_prd, "") or "")
        arch_ref = str(row.get(col_arch, "") or "")
        ui_ref   = str(row.get(col_ui, "") or "") if col_ui else ""

        prd_num  = parse_ref_number(prd_ref)
        arch_num = parse_ref_number(arch_ref)
        ui_num   = parse_ref_number(ui_ref) if ui_ref else None

        prd_ok  = (prd_num  in prd_sections)  if prd_num  else False
        arch_ok = (arch_num in arch_sections) if arch_num else False
        ui_ok   = (ui_num   in ui_sections)   if ui_num   else (False if col_ui else True)  # if no UI col, treat as pass

        # Aggregate status
        if prd_ok and arch_ok and ui_ok:
            status = "OK"
        else:
            parts = []
            if not prd_ok:  parts.append("PRD")
            if not arch_ok: parts.append("ARCH")
            if col_ui and not ui_ok: parts.append("UI")
            status = "MISMATCH[" + ",".join(parts) + "]"

        rows.append({
            "ID": rid,
            "Flow": flow,
            "PRD_Ref": prd_ref,   "PRD_Section": prd_num or "",   "PRD_found": prd_ok,
            "Arch_Ref": arch_ref, "Arch_Section": arch_num or "", "Arch_found": arch_ok,
            "UI_Ref": ui_ref,     "UI_Section": ui_num or "",     "UI_found": ui_ok if col_ui else "",
            "Status": status
        })

    out = pd.DataFrame(rows)
    out.to_csv(out_csv, index=False)
    print(f"[DONE] Report written: {out_csv}")

if __name__ == "__main__":
    main()
