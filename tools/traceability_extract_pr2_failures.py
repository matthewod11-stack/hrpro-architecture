import csv
from pathlib import Path

PR2_FEATURES = [
    "Advisor SSE streaming UI integration",
    "Citation chips + drawer (a11y)",
    "Export Summary (PDF) button",
    "Telemetry dashboard",
    "E2E demo script",
]

CSV_PATH = Path("docs/traceability/Traceability_link_check.csv")

HEADER_ALIASES = {
    "feature name": ["feature name", "feature", "featurename"],
    "prd reference": ["prd reference", "prd", "prd ref"],
    "arch reference": ["arch reference", "arch", "arch ref"],
    "ui reference": ["ui reference", "ui", "ui ref"],
    "status": ["status"],
}


def normalize_header(h):
    return h.strip().lower().replace(" ", "").replace("_", "")


def find_header(headers, aliases):
    for alias in aliases:
        norm_alias = normalize_header(alias)
        for i, h in enumerate(headers):
            if normalize_header(h) == norm_alias:
                return i
    return None


def main():
    if not CSV_PATH.exists():
        print(f"CSV not found: {CSV_PATH}")
        return
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        print("CSV is empty.")
        return
    headers = rows[0]
    idx_map = {}
    for key, aliases in HEADER_ALIASES.items():
        idx = find_header(headers, aliases)
        if idx is not None:
            idx_map[key] = idx
    prd_diag_idx = find_header(headers, ["prd_diag"])
    arch_diag_idx = find_header(headers, ["arch_diag"])
    ui_diag_idx = find_header(headers, ["ui_diag"])
    found = False
    for i, row in enumerate(rows[1:], start=2):
        feat = (
            row[idx_map.get("feature name", -1)].strip().lower()
            if idx_map.get("feature name", -1) != -1
            else ""
        )
        if any(feat == f.lower() for f in PR2_FEATURES):
            status = (
                row[idx_map.get("status", -1)]
                if idx_map.get("status", -1) != -1
                else ""
            )
            fail = (
                status.lower() != "ok"
                or "mismatch" in status.lower()
                or "missing" in status.lower()
            )
            if not fail:
                for cell in row:
                    if "mismatch" in cell.lower() or "missing" in cell.lower():
                        fail = True
                        break
            if fail:
                found = True
                prd_val = (
                    row[idx_map.get("prd reference", -1)]
                    if idx_map.get("prd reference", -1) != -1
                    else ""
                )
                arch_val = (
                    row[idx_map.get("arch reference", -1)]
                    if idx_map.get("arch reference", -1) != -1
                    else ""
                )
                ui_val = (
                    row[idx_map.get("ui reference", -1)]
                    if idx_map.get("ui reference", -1) != -1
                    else ""
                )
                prd_diag = (
                    row[prd_diag_idx]
                    if prd_diag_idx is not None and prd_diag_idx < len(row)
                    else prd_val
                )
                arch_diag = (
                    row[arch_diag_idx]
                    if arch_diag_idx is not None and arch_diag_idx < len(row)
                    else arch_val
                )
                ui_diag = (
                    row[ui_diag_idx]
                    if ui_diag_idx is not None and ui_diag_idx < len(row)
                    else ui_val
                )
                print("----")
                print(f"Feature: {row[idx_map.get('feature name', -1)]}")
                print(f"Status: {status}")
                print(f"PRD: {prd_val}   ➜ {prd_diag}")
                print(f"Arch: {arch_val} ➜ {arch_diag}")
                print(f"UI: {ui_val}     ➜ {ui_diag}")
                print(f"Row: {i}")
    if not found:
        print("No failing PR-2 rows.")


if __name__ == "__main__":
    main()
