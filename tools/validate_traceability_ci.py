import csv
import subprocess
import sys


def main():
    # Run validator
    result = subprocess.run(
        [
            sys.executable,
            "tools/validate_traceability_md.py",
            "--prd",
            "docs/PRD/PRD_v4.0_unified_numbered.md",
            "--arch",
            "docs/Architecture/Architecture_v4.1_unified.md",
            "--ui",
            "docs/UIFramework/UIFramework_v4.0_unified_numbered.md",
            "--trace",
            "docs/traceability/Traceability_v4.1_prefilled.xlsx",
            "--out",
            "docs/traceability/Traceability_link_check.csv",
        ]
    )
    waived = 0
    fails = 0
    total = 0
    with open("docs/traceability/Traceability_link_check.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        hdr = next(reader)
        status_idx = None
        tag_idx = None
        for i, h in enumerate(hdr):
            h_norm = h.strip().lower().replace(" ", "").replace("_", "")
            if h_norm == "status":
                status_idx = i
            if h_norm == "tag":
                tag_idx = i
        for row in reader:
            total += 1
            status = (
                row[status_idx].lower()
                if status_idx is not None and len(row) > status_idx
                else ""
            )
            tag = (
                row[tag_idx].lower()
                if tag_idx is not None and len(row) > tag_idx
                else ""
            )
            if status != "ok":
                if "legacy-waived" in tag:
                    waived += 1
                else:
                    fails += 1
    print(f"CI Gate: fails={fails} (excluding waived), waived={waived}, total={total}")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
