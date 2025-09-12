import requests
import yaml
import sys

with open("config/retrieval.yaml") as f:
    cfg = yaml.safe_load(f)
endpoint = cfg.get("ollama", {}).get("endpoint", "http://localhost:11434")
model = cfg.get("ollama", {}).get("model", "mxbai-embed-large")
try:
    resp = requests.get(f"{endpoint}/api/tags", timeout=10)
    resp.raise_for_status()
    tags = resp.json().get("models", [])
    print(f"Ollama endpoint OK: {endpoint}")
    print(f"Available models: {[m['name'] for m in tags]}")
    print(f"Configured model: {model}")
except Exception as e:
    print(f"Ollama endpoint check failed: {e}")
    sys.exit(1)
