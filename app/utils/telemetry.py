from datetime import datetime
import json
import os


def log(event: dict):
    """Persist an event dictionary to a JSON lines telemetry log."""
    try:
        os.makedirs("logs", exist_ok=True)
        event["timestamp"] = datetime.utcnow().isoformat() + "Z"
        with open("logs/dev_telemetry.jsonl", "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"[telemetry] Logging failed: {e}")
