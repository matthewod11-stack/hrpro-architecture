import argparse
import json

from app.retrieval.adapter import retrieve

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()
    results = retrieve(args.topic, args.top_k)
    print(f"{'Rank':<4} {'Score':<6} Doc::Anchor Section")
    for i, r in enumerate(results):
        print(f"{i+1:<4} {r['score']:.3f}  {r['doc']}::{r['anchor']} {r['section']}")
    with open("last_query.json", "w") as f:
        json.dump(results, f, indent=2)
