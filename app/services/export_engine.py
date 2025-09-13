import hashlib
import json
from pathlib import Path
import time


def _ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _brand_check(branding: dict) -> tuple[bool, list[str]]:
    issues = []
    if not branding.get("client_name"):
        issues.append("missing_client_name")
    lp = branding.get("logo_path")
    if lp and not Path(lp).exists():
        issues.append("logo_not_found")
    return (len(issues) == 0, issues)


def _manifest_hash(payload: dict, outfile: Path) -> str:
    h = hashlib.sha256()
    stable = {k: payload[k] for k in ["trace_id", "client", "module", "title"]}
    h.update(json.dumps(stable, sort_keys=True).encode())
    if outfile.exists():
        h.update(outfile.read_bytes())
    return h.hexdigest()


def render_pdf(req: dict) -> tuple[str, bool, str]:
    base = Path("artifacts") / req["client"] / _ts()
    base.mkdir(parents=True, exist_ok=True)
    out = base / (req["title"].replace(" ", "_") + ".pdf")
    out.write_text(
        f"# {req['title']}\n\nCLIENT: {req['branding'].get('client_name')}\nTRACE: {req['trace_id']}\n\n{req['content']}\n\nFOOTER: Generated with HRPro • Confidential • {time.ctime()}\n",
        encoding="utf-8",
    )
    ok, _ = _brand_check(req["branding"])
    mh = _manifest_hash(req, out)
    # Telemetry
    try:
        with open("logs/export.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "trace_id": req["trace_id"],
                        "path": str(out),
                        "ok": ok,
                        "manifest": mh,
                        "module": req["module"],
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    return (str(out), ok, mh)


def render_csv(req: dict) -> tuple[str, bool, str]:
    base = Path("artifacts") / req["client"] / _ts()
    base.mkdir(parents=True, exist_ok=True)
    out = base / (req["title"].replace(" ", "_") + ".csv")
    out.write_text(req["content"], encoding="utf-8")
    ok, _ = _brand_check(req["branding"])
    mh = _manifest_hash(req, out)
    # Telemetry
    try:
        with open("logs/export.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "trace_id": req["trace_id"],
                        "path": str(out),
                        "ok": ok,
                        "manifest": mh,
                        "module": req["module"],
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    return (str(out), ok, mh)
