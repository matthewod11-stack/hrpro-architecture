from pathlib import Path
from datetime import datetime

# Dummy data for illustration
summary = {
    "overall": True,
    "token": True,
    "json": True,
    "acceptance": False,
    "export": True,
    "counts": {"pass": 3, "fail": 1},
}
checks = [
    {"section": "Token", "name": "Design tokens", "result": True},
    {"section": "JSON", "name": "Export contract", "result": True},
    {"section": "Acceptance", "name": "ADR-0005", "result": False},
    {"section": "Export", "name": "Manifest hash", "result": True},
]

md_path = Path("docs/traceability/validator_summary.md")
html_path = Path("docs/traceability/validator_summary.html")

# Markdown front-matter
md = f"""
---
overall: {'✅' if summary['overall'] else '❌'}
pass: {summary['counts']['pass']}
fail: {summary['counts']['fail']}
date: {datetime.now().isoformat()}
---

# Validator Summary
"""

sections = ["Token", "JSON", "Acceptance", "Export"]
for section in sections:
    md += f"\n## {section} Checks\n"
    md += "| Name | Result |\n|---|---|\n"
    for c in checks:
        if c["section"] == section:
            md += f"| {c['name']} | {'✅' if c['result'] else '❌'} |\n"

md_path.parent.mkdir(parents=True, exist_ok=True)
md_path.write_text(md)

# HTML output
html = f"""
<html><head><meta charset='utf-8'><title>Validator Summary</title>
<style>
body{{font-family:sans-serif;background:#f7f8fa;color:#222;}}
table{{border-collapse:collapse;width:100%;margin-bottom:24px;}}
th,td{{border:1px solid #e0e3e8;padding:8px;}}
th{{background:#f0f0f0;}}
.pass{{color:#4B5AEF;font-weight:bold;}}
.fail{{color:#d4380d;font-weight:bold;}}
</style></head><body>
<h1>Validator Summary</h1>
<div><b>Overall:</b> {'✅' if summary['overall'] else '❌'} | <b>Pass:</b> {summary['counts']['pass']} | <b>Fail:</b> {summary['counts']['fail']} | <b>Date:</b> {datetime.now().isoformat()}</div>
"""
for section in sections:
    html += f"<h2>{section} Checks</h2><table><tr><th>Name</th><th>Result</th></tr>"
    for c in checks:
        if c["section"] == section:
            html += f"<tr><td>{c['name']}</td><td class={'pass' if c['result'] else 'fail'}>{'✅' if c['result'] else '❌'}</td></tr>"
    html += "</table>"
html += "</body></html>"
html_path.write_text(html)
