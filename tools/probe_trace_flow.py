import argparse
import sys
import uuid

import requests

API_BASE = "http://localhost:8000/v1/export/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", choices=["pip", "306090"], required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--export", choices=["pdf", "xlsx", "csv"], required=True)
    args = parser.parse_args()

    trace_id = "probe-" + uuid.uuid4().hex[:12]
    payload = {
        "content": {"dummy": True},
        "module": args.module,
        "client": args.client,
        "trace_id": trace_id,
    }
    resp = requests.post(API_BASE + args.export, json=payload)
    try:
        data = resp.json()
    except Exception:
        print("Invalid JSON response", file=sys.stderr)
        sys.exit(2)
    print(data)
    ok = (
        data.get("trace_id") == trace_id
        and data.get("export_branding_compliance") is True
        and isinstance(data.get("export_manifest_hash"), str)
        and len(data["export_manifest_hash"]) == 64
        and all(c in "0123456789abcdef" for c in data["export_manifest_hash"])
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
