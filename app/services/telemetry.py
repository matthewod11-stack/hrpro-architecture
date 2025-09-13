import json
from pathlib import Path
import time
from typing import Any

LOG_DIR = Path("telemetry")
LOG_DIR.mkdir(exist_ok=True, parents=True)


def _log_path(name: str) -> Path:
    return LOG_DIR / f"{name}.jsonl"


def emit(name: str, payload: dict[str, Any]) -> None:
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **payload}
    p = _log_path(name)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def tail(name: str, n: int = 200) -> list[dict[str, Any]]:
    p = _log_path(name)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()[-n:]
    return [json.loads(x) for x in lines if x.strip()]


def rotate(name: str, keep: int = 5) -> None:
    p = _log_path(name)
    if not p.exists() or p.stat().st_size < 10 * 1024 * 1024:
        return
    ts = time.strftime("%Y%m%d-%H%M%S")
    p.rename(p.with_suffix(f".{ts}.jsonl"))
    archives = sorted(LOG_DIR.glob(f"{name}.jsonl.*"), reverse=True)
    for old in archives[keep:]:
        old.unlink(missing_ok=True)
