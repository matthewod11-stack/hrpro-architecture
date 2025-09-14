from __future__ import annotations

from collections.abc import Iterator
import json
import time

import requests


def stream_sse(url: str, body: dict, timeout_s: int = 60) -> Iterator[dict]:
    """Yield parsed Server-Sent Events with automatic retries."""
    max_retries = 2
    last_err = None
    for attempt in range(max_retries):
        try:
            with requests.post(
                url, json=body, stream=True, timeout=(10, timeout_s)
            ) as r:
                r.raise_for_status()
                cur: dict[str, object] = {}
                for raw in r.iter_lines(decode_unicode=True):
                    if raw is None or not raw.strip():
                        if cur:
                            yield cur
                            cur = {}
                        continue
                    if raw.startswith("event: "):
                        cur["event"] = raw.split("event: ", 1)[1].strip()
                    elif raw.startswith("data: "):
                        try:
                            data_val = raw.split("data: ", 1)[1]
                            cur["data"] = (
                                json.loads(data_val) if data_val.strip() else {}
                            )
                        except Exception:
                            cur["data"] = {}
                if cur:
                    yield cur
            return
        except (requests.exceptions.RequestException, AssertionError) as e:
            last_err = e
            time.sleep(0.2 + 0.2 * attempt)
    if last_err:
        raise RuntimeError(f"SSE failed after {max_retries} attempts: {last_err}")
