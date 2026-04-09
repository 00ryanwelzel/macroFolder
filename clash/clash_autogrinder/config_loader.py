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
    if not path.exists():
        raise FileNotFoundError(f"File not found at {Path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as err:
        raise SyntaxError(err)

    except OSError as err:
        raise FileNotFoundError(err)

    validate_config(data, path)
    return data


def validate_config(data: dict, path: Path | str = "config") -> None:
    if not isinstance(data, dict):
        raise SyntaxError(f"{path} must be a JSON object")

    for key, value in data.items():
        if not isinstance(key, str):
            raise SyntaxError(f"All keys in {path} must be strings")

        if not isinstance(value, list):
            raise SyntaxError(f"{path}.{key} must be a list like [x, y]")

        if len(value) != 2:
            raise SyntaxError(f"{path}.{key} must contain exactly 2 values")

        x, y = value

        if x is not None and not isinstance(x, int):
            raise SyntaxError(f"{path}.{key}[0] must be an int or null")

        if y is not None and not isinstance(y, int):
            raise SyntaxError(f"{path}.{key}[1] must be an int or null")


def get_position(config: dict, name: str) -> tuple[int, int] | None:
    if name not in config:
        raise FileNotFoundError(f"{name} not found in config")

    x, y = config[name]

    if x is None or y is None:
        return None

    return x, y

# ----------------------
# --- Main Functions ---
# ----------------------


def load_button_config() -> dict:
    return load_json_config(BUTTON_CONFIG_PATH)


def load_window_config() -> dict:
    return load_json_config(WINDOW_CONFIG_PATH)


def load_map_config() -> dict:
    return load_json_config(MAP_CONFIG_PATH)
