import json
from pathlib import Path

TOKENS_PATH = Path(__file__).parent / "tokens.json"


def load_tokens():
    with open(TOKENS_PATH) as f:
        return json.load(f)


def get_palette():
    tokens = load_tokens()
    mode = tokens.get("mode", "light")
    theme = tokens["themes"].get(mode, {})
    palette = {**tokens, **theme}
    return palette


def set_mode(mode: str):
    tokens = load_tokens()
    tokens["mode"] = mode
    with open(TOKENS_PATH, "w") as f:
        json.dump(tokens, f, indent=2)
