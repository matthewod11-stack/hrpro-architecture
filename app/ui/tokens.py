# UI token constants
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
RADIUS_SM = 6
RADIUS_MD = 12
FG_MUTED = "#6B7280"
BG_SURFACE = "#F7F8FA"
BG_CARD = "#fff"
BORDER_MID = "#E0E3E8"
import json
from pathlib import Path

TOKENS_PATH = Path(__file__).parent / "tokens.json"


def load_tokens():
    with open(TOKENS_PATH) as f:
        return json.load(f)


# UI token constants
SPACE_MD = 16
RADIUS_SM = 6
FG_MUTED = "#888"


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
