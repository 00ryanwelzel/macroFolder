import threading
import time

import input_handler
from clash_autogrinder import clash_autogrinder
from constants import Hotkeys, PollTimes


def main() -> int:
    stop_event = threading.Event()
    worker_thread: threading.Thread | None = None

    start_hotkey_was_pressed = False
    stop_hotkey_was_pressed = False
    end_hotkey_was_pressed = False
    coords_hotkey_was_pressed = False

    while True:
        start_hotkey_pressed = input_handler.is_all_keys_down(Hotkeys.start_hotkey)
        stop_hotkey_pressed = input_handler.is_all_keys_down(Hotkeys.stop_hotkey)
        end_hotkey_pressed = input_handler.is_all_keys_down(Hotkeys.end_hotkey)
        coords_hotkey_pressed = input_handler.is_all_keys_down(Hotkeys.coords_hotkey)

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

        if coords_hotkey_pressed and not coords_hotkey_was_pressed and not worker_is_running:
            print(input_handler.isat())

        start_hotkey_was_pressed = start_hotkey_pressed
        stop_hotkey_was_pressed = stop_hotkey_pressed
        end_hotkey_was_pressed = end_hotkey_pressed
        coords_hotkey_was_pressed = coords_hotkey_pressed

        time.sleep(PollTimes.hotkey_poll)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
