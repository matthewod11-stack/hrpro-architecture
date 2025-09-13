from __future__ import annotations

from collections.abc import Iterator
import json
import time

import requests


def stream_sse(
    url: str, body: dict, timeout_s: int = 60, max_retries: int = 2
) -> Iterator[dict]:
    last_err = None
    for attempt in range(max_retries):
        try:
            with requests.post(
                url, json=body, stream=True, timeout=(10, timeout_s)
            ) as r:
                r.raise_for_status()
                cur = {}
                for raw in r.iter_lines(decode_unicode=True):
                    if raw is None or not raw.strip():
                        if cur:
                            yield cur
                            cur = {}
                        continue
                    # Ignore stray lines
                    if raw.startswith("event: "):
                        cur["event"] = raw.split("event: ", 1)[1].strip()
                    elif raw.startswith("data: "):
                        try:
                            data_val = raw.split("data: ", 1)[1]
                            # tolerate empty delta payloads
                            cur["data"] = (
                                json.loads(data_val) if data_val.strip() else {}
                            )
                        except Exception:
                            cur["data"] = {}
                    # else: ignore stray lines
                if cur:
                    yield cur
            return
        except (requests.exceptions.RequestException, AssertionError) as e:
            last_err = e
            time.sleep(0.2 + 0.2 * attempt)
    # Never throw on partial frames, but raise if no connection
    if last_err:
        raise RuntimeError(f"SSE failed after {max_retries} attempts: {last_err}")


def stream_sse(url: str, json_body: dict, timeout_s: int = 30) -> Iterator[dict]:
    try:
        with requests.post(
            url, json=json_body, stream=True, timeout=(10, timeout_s)
        ) as resp:
            trace_id = None
            for line in resp.iter_lines():
                if isinstance(line, bytes):
                    line = line.decode()
                if line.startswith("data: "):
                    try:
                        evt = json.loads(line[6:])
                        trace_id = evt.get("trace_id", trace_id)
                        yield evt
                    except Exception as e:
                        yield {
                            "event": "error",
                            "message": str(e),
                            "trace_id": trace_id,
                        }
                elif line.strip() == "":
                    continue
    except Exception as e:
        yield {"event": "error", "message": str(e), "trace_id": None}
