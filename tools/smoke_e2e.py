#!/usr/bin/env python
import json
import os
from pathlib import Path

import requests

API = os.environ.get("HRPRO_API", "http://localhost:8000")


def sse_post(url, body):
    with requests.post(url, json=body, stream=True, timeout=(10, 60)) as r:
        r.raise_for_status()
        cur = {}
        for line in r.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line.startswith("event: "):
                cur["event"] = line[7:].strip()
            elif line.startswith("data: "):
                cur["data"] = json.loads(line[6:])
            elif line.strip() == "":
                if cur:
                    yield cur
                    cur = {}
        if cur:
            yield cur


def main():
    events = list(
        sse_post(f"{API}/v1/advisor/answer", {"query": "How do we enforce citations?"})
    )
    start = next(x for x in events if x.get("event") == "start")
    final = next(x for x in events if x.get("event") == "final")
    trace = start["data"]["trace_id"]
    cits = final["data"]["answer"].get("citations", [])
    # export
    payload = {
        "trace_id": trace,
        "client": "demo",
        "module": "advisor",
        "title": "Advisor Summary",
        "content": final["data"]["answer"].get("summary", ""),
        "branding": {"client_name": "DEMO", "watermark": "Sandbox"},
    }
    r = requests.post(f"{API}/v1/export/pdf", json=payload, timeout=30)
    path = r.json()["path"]
    assert Path(path).exists()
    print(f"E2E OK • trace={trace} • citations={len(cits)} • export={path}")


if __name__ == "__main__":
    raise SystemExit(main())  #!/usr/bin/env python
import os
import sys

API = os.environ.get("HRPRO_API", "http://localhost:8000")


def sse_post(url, body):
    with requests.post(url, json=body, stream=True, timeout=(10, 60)) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith(b"data: "):
                yield json.loads(line[6:].decode())


def main():
    # 1) Advisor stream
    q = {"query": "How do we enforce citations?", "persona": "cpo", "top_k": 2}
    final = None
    trace = None
    for evt in sse_post(f"{API}/v1/advisor/answer", q):
        if not trace and "trace_id" in evt:
            trace = evt["trace_id"]
        if evt.get("event") == "final":
            final = evt["answer"]
            break
        if evt.get("event") == "error":
            print("Advisor error:", evt.get("message"))
            return 2
    if not final:
        print("No final advisor answer")
        return 2
    cits = final.get("citations", [])
    if not cits:
        print("No citations in final answer")
        return 3
    summary = final.get("summary") or ""
    # 2) Export
    payload = {
        "trace_id": trace or "adv_demo",
        "client": "demo",
        "module": "advisor",
        "title": "Advisor Summary",
        "content": summary or "No summary",
        "branding": {"client_name": "DEMO", "watermark": "Sandbox"},
    }
    r = requests.post(f"{API}/v1/export/pdf", json=payload, timeout=30)
    r.raise_for_status()
    resp = r.json()
    path = resp["path"]
    ok = resp["export_branding_compliance"]
    if not Path(path).exists():
        print("Export path missing:", path)
        return 4
    # 3) Telemetry
    adv_log = Path("telemetry/advisor.jsonl")
    exp_log = Path("telemetry/export.jsonl")
    if not adv_log.exists() or not exp_log.exists():
        print("Telemetry logs missing")
        return 5
    adv_lines = adv_log.read_text().splitlines()[-100:]
    exp_lines = exp_log.read_text().splitlines()[-100:]
    assert any(
        (trace or "") in ln for ln in adv_lines
    ), "Trace not in advisor telemetry"
    assert any((trace or "") in ln for ln in exp_lines), "Trace not in export telemetry"

    print(
        f"E2E OK • trace={trace} • citations={len(cits)} • export={path} • branding_ok={ok}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
