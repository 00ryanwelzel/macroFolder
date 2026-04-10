import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUTTON_CONFIG_PATH = PROJECT_ROOT / "configs" / "button_config.json"
WINDOW_CONFIG_PATH = PROJECT_ROOT / "configs" / "window_config.json"
MAP_CONFIG_PATH = PROJECT_ROOT / "configs" / "map_config.json"

if not BUTTON_CONFIG_PATH.exists() or not WINDOW_CONFIG_PATH.exists() or not MAP_CONFIG_PATH.exists():
    raise FileNotFoundError("Missing one or more of required configs.")

# ---------------
# --- Helpers ---
# ---------------


def load_json_config(path: Path) -> dict:
    # Load a config file, parse its JSON, and validate the expected structure.
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as err:
        raise SyntaxError(err)

    return data


def load_window_json_config(path: Path) -> dict:
    # Load a window config file, parse its JSON, and validate the expected structure.
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as err:
        raise SyntaxError(err)

    return data

# ----------------------
# --- Main Functions ---
# ----------------------


def load_button_config() -> dict:
    return load_json_config(BUTTON_CONFIG_PATH)


def load_window_config() -> dict:
    return load_window_json_config(WINDOW_CONFIG_PATH)


def load_map_config() -> dict:
    return load_json_config(MAP_CONFIG_PATH)
