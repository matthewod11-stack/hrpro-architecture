#!/usr/bin/env python
import argparse
import json
from pathlib import Path
import time

from app.schemas.advisor import AdvisorQuery
from app.services.advisor_orchestrator import stream_advisor_answer


def run_one(q, must_anchor):
    trace = f"eval_{int(time.time()*1000)}"
    gen = stream_advisor_answer(AdvisorQuery(query=q, top_k=6), trace)
    final = None
    for evt in gen:
        if evt.get("event") == "final":
            final = evt["answer"]
            break
    ok = False
    found = [c["anchor"] for c in final.get("citations", [])]
    ok = any(a.startswith(must_anchor) for a in found)
    return {"trace_id": trace, "ok": ok, "anchors": found}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goldens", default="evals/goldens/advisor_qa.jsonl")
    ap.add_argument("--out", default="evals/results/advisor_eval.jsonl")
    args = ap.parse_args()

    Path("evals/results").mkdir(parents=True, exist_ok=True)
    goods = [
        json.loads(l) for l in Path(args.goldens).read_text().splitlines() if l.strip()
    ]
    results = []
    for g in goods:
        r = run_one(g["query"], g["must_anchor"])
        r.update({"qid": g["qid"]})
        results.append(r)
        print(json.dumps(r))
    Path(args.out).write_text("\n".join(json.dumps(x) for x in results))
    passed = sum(1 for x in results if x["ok"])
    total = len(results)
    print(f"PASS {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
