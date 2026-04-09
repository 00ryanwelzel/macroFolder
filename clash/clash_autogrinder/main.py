from __future__ import annotations

import ctypes
import threading
import time
from dataclasses import dataclass


VK_CODES: dict[str, int] = {
    "alt": 0x12,
    "ctrl": 0x11,
    "shift": 0x10,
    "enter": 0x0D,
    "esc": 0x1B,
    "space": 0x20,
    "tab": 0x09,
}


@dataclass(frozen=True)
class SleepTimes:
    user_input: float = 0.10
    hotkey_poll: float = 0.05


@dataclass(frozen=True)
class Hotkeys:
    start_hotkey: tuple[str, str, str] = ("ctrl", "shift", "1")
    stop_hotkey: tuple[str, str, str] = ("ctrl", "shift", "2")
    end_hotkey: tuple[str, str, str] = ("ctrl", "shift", "3")


SLEEP_TIMES = SleepTimes()
HOTKEYS = Hotkeys()


def virtual_key_code(key: str) -> int:
    # Convert a hotkeys into a Windows keyboard APIs keycode.
    normalized_key = key.lower()

    if normalized_key in VK_CODES:
        return VK_CODES[normalized_key]

    if len(normalized_key) == 1 and normalized_key.isalnum():
        return ord(normalized_key.upper())

    raise ValueError(f"Unsupported hotkey key: {key}")


def check_hotkey(hotkey: tuple[str, str, str]) -> bool:
    # Return True only when every key in the hotkey tuple is currently held.
    currently_pressed_flag = 0x8000
    return all(ctypes.windll.user32.GetAsyncKeyState(virtual_key_code(key)) & currently_pressed_flag for key in hotkey)


def clash_autogrinder(stop_event: threading.Event) -> None:
    # Worker thread entrypoint. This loop keeps running until `main()`
    # signals the thread to stop through the shared event object.
    while not stop_event.is_set():
        print("abs")
        # Placeholder for the actual grind step implementation.
        time.sleep(SLEEP_TIMES.user_input)


def main() -> int:
    # Main thread: watch for hotkeys, start the worker thread, stop it,
    # and allow the program to exit once the worker is no longer running.
    stop_event = threading.Event()
    worker_thread: threading.Thread | None = None

    start_hotkey_was_pressed = False
    stop_hotkey_was_pressed = False
    end_hotkey_was_pressed = False

    while True:
        start_hotkey_pressed = check_hotkey(HOTKEYS.start_hotkey)
        stop_hotkey_pressed = check_hotkey(HOTKEYS.stop_hotkey)
        end_hotkey_pressed = check_hotkey(HOTKEYS.end_hotkey)

        worker_is_running = worker_thread is not None and worker_thread.is_alive()

        if start_hotkey_pressed and not start_hotkey_was_pressed and not worker_is_running:
            stop_event = threading.Event()
            worker_thread = threading.Thread(
                target=clash_autogrinder,
                args=(stop_event,),
                name="clash-autogrinder",
                daemon=True,
            )
            worker_thread.start()

        worker_is_running = worker_thread is not None and worker_thread.is_alive()

        if stop_hotkey_pressed and not stop_hotkey_was_pressed and worker_is_running:
            stop_event.set()
            worker_thread.join()
            worker_thread = None
            worker_is_running = False

        if end_hotkey_pressed and not end_hotkey_was_pressed and not worker_is_running:
            break

        start_hotkey_was_pressed = start_hotkey_pressed
        stop_hotkey_was_pressed = stop_hotkey_pressed
        end_hotkey_was_pressed = end_hotkey_pressed

        time.sleep(SLEEP_TIMES.hotkey_poll)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
