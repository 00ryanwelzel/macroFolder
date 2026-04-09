import ctypes
import time


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


USER32 = ctypes.windll.user32

KEY_PRESSED_FLAG = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

VIRTUAL_KEY_CODES: dict[str, int] = {
    "backspace": 0x08,
    "break": 0x03,
    "cancel": 0x03,
    "tab": 0x09,
    "clear": 0x0C,
    "enter": 0x0D,
    "return": 0x0D,
    "alt": 0x12,
    "ctrl": 0x11,
    "shift": 0x10,
    "pause": 0x13,
    "capslock": 0x14,
    "caps_lock": 0x14,
    "kana": 0x15,
    "hangul": 0x15,
    "ime_on": 0x16,
    "junja": 0x17,
    "final": 0x18,
    "hanja": 0x19,
    "kanji": 0x19,
    "ime_off": 0x1A,
    "esc": 0x1B,
    "escape": 0x1B,
    "convert": 0x1C,
    "nonconvert": 0x1D,
    "accept": 0x1E,
    "modechange": 0x1F,
    "space": 0x20,
    "pageup": 0x21,
    "page_up": 0x21,
    "prior": 0x21,
    "pagedown": 0x22,
    "page_down": 0x22,
    "next": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "select": 0x29,
    "print": 0x2A,
    "execute": 0x2B,
    "printscreen": 0x2C,
    "print_screen": 0x2C,
    "snapshot": 0x2C,
    "insert": 0x2D,
    "delete": 0x2E,
    "del": 0x2E,
    "help": 0x2F,
    "lwin": 0x5B,
    "left_win": 0x5B,
    "rwin": 0x5C,
    "right_win": 0x5C,
    "apps": 0x5D,
    "menu": 0x5D,
    "sleep": 0x5F,
    "numpad0": 0x60,
    "numpad1": 0x61,
    "numpad2": 0x62,
    "numpad3": 0x63,
    "numpad4": 0x64,
    "numpad5": 0x65,
    "numpad6": 0x66,
    "numpad7": 0x67,
    "numpad8": 0x68,
    "numpad9": 0x69,
    "multiply": 0x6A,
    "add": 0x6B,
    "separator": 0x6C,
    "subtract": 0x6D,
    "decimal": 0x6E,
    "divide": 0x6F,
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B,
    "f13": 0x7C,
    "f14": 0x7D,
    "f15": 0x7E,
    "f16": 0x7F,
    "f17": 0x80,
    "f18": 0x81,
    "f19": 0x82,
    "f20": 0x83,
    "f21": 0x84,
    "f22": 0x85,
    "f23": 0x86,
    "f24": 0x87,
    "numlock": 0x90,
    "num_lock": 0x90,
    "scrolllock": 0x91,
    "scroll_lock": 0x91,
    "lshift": 0xA0,
    "left_shift": 0xA0,
    "rshift": 0xA1,
    "right_shift": 0xA1,
    "lctrl": 0xA2,
    "left_ctrl": 0xA2,
    "rctrl": 0xA3,
    "right_ctrl": 0xA3,
    "lalt": 0xA4,
    "left_alt": 0xA4,
    "ralt": 0xA5,
    "right_alt": 0xA5,
    "browser_back": 0xA6,
    "browser_forward": 0xA7,
    "browser_refresh": 0xA8,
    "browser_stop": 0xA9,
    "browser_search": 0xAA,
    "browser_favorites": 0xAB,
    "browser_home": 0xAC,
    "volume_mute": 0xAD,
    "volume_down": 0xAE,
    "volume_up": 0xAF,
    "media_next_track": 0xB0,
    "media_prev_track": 0xB1,
    "media_stop": 0xB2,
    "media_play_pause": 0xB3,
    "launch_mail": 0xB4,
    "launch_media_select": 0xB5,
    "launch_app1": 0xB6,
    "launch_app2": 0xB7,
    "semicolon": 0xBA,
    "plus": 0xBB,
    "comma": 0xBC,
    "minus": 0xBD,
    "period": 0xBE,
    "slash": 0xBF,
    "grave": 0xC0,
    "backtick": 0xC0,
    "left_bracket": 0xDB,
    "backslash": 0xDC,
    "right_bracket": 0xDD,
    "apostrophe": 0xDE,
    "quote": 0xDE,
    "oem_8": 0xDF,
    "oem_102": 0xE2,
    "processkey": 0xE5,
    "process_key": 0xE5,
    "packet": 0xE7,
    "attn": 0xF6,
    "crsel": 0xF7,
    "exsel": 0xF8,
    "ereof": 0xF9,
    "play": 0xFA,
    "zoom": 0xFB,
    "noname": 0xFC,
    "pa1": 0xFD,
    "oem_clear": 0xFE,
}

CLICKSLEEP = 0.01


def virtual_key_code(key: str) -> int:
    # Convert a hotkeys into a Windows keyboard APIs keycode.
    normalized_key = key.lower()

    if normalized_key in VIRTUAL_KEY_CODES:
        return VIRTUAL_KEY_CODES[normalized_key]

    if len(normalized_key) == 1 and normalized_key.isalnum():
        return ord(normalized_key.upper())

    raise ValueError(f"Unsupported hotkey key: {key}")


def is_key_down(key: str) -> bool:
    return bool(USER32.GetAsyncKeyState(virtual_key_code(key)) & KEY_PRESSED_FLAG)


def is_hotkey_down(hotkey: tuple[str, ...]) -> bool:
    return all(is_key_down(key) for key in hotkey)

# ------------------------
# --- Cursor Functions ---
# ------------------------


def cursor_moveto(moveto: tuple[int, int], over: float) -> None:
    start_x, start_y = cursor_isat()
    end_x, end_y = moveto

    if over <= 0:
        USER32.SetCursorPos(end_x, end_y)
        return

    step_duration = 0.01
    steps = max(1, int(over / step_duration))

    for step in range(1, steps + 1):
        progress = step / steps
        next_x = round(start_x + (end_x - start_x) * progress)
        next_y = round(start_y + (end_y - start_y) * progress)
        USER32.SetCursorPos(next_x, next_y)
        time.sleep(over / steps)


def cursor_isat() -> tuple[int, int]:
    point = Point(0, 0)
    USER32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

# -----------------------
# --- Mouse Functions ---
# -----------------------


def leftmousedown() -> None:
    USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def leftmouseup() -> None:
    USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def rightmousedown() -> None:
    USER32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)


def rightmouseup() -> None:
    USER32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def cursor_leftclick() -> None:
    leftmousedown()
    time.sleep(CLICKSLEEP)
    leftmouseup()


def cursor_rightclick() -> None:
    rightmousedown()
    time.sleep(CLICKSLEEP)
    rightmouseup()

# ------------------------
# --- Scroll Functions ---
# ------------------------


def scroll(delta: int, over: float) -> None:
    if over <= 0:
        USER32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        return

    step_duration = 0.05
    steps = max(1, int(over / step_duration))

    for _ in range(steps):
        USER32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        time.sleep(over / steps)


def scrolldown(steps: int, over: float) -> None:
    scroll(-steps * WHEEL_DELTA, over)


def scrollup(steps: int, over: float) -> None:
    scroll(steps * WHEEL_DELTA, over)
