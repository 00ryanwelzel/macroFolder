import threading
import time

import image_handler
import config_handler
import input_controller

from dataclasses import (dataclass)


@dataclass(frozen=True)
class Times:
    instant: float = 0.01
    action_time: float = 0.5
    find_attack_time: float = 3.5
    scroll_time: float = 1
    troop_drag_time: float = 7
    destruction_check_time: float = 5

    user_input: float = 0.10
    hotkey_poll: float = 0.05


@dataclass(frozen=True)
class Hotkeys:
    start_hotkey: tuple[str, ...] = ("ctrl", "alt", "1")
    stop_hotkey: tuple[str, ...] = ("ctrl", "alt", "2")
    end_hotkey: tuple[str, ...] = ("ctrl", "alt", "3")
    coords_hotkey: tuple[str, ...] = ("ctrl", "alt", "4")


TIMES = Times()
HOTKEYS = Hotkeys()

BUTTON_CONFIG = config_handler.load_button_config()
WINDOW_CONFIG = config_handler.load_window_config()
MAP_CONFIG = config_handler.load_map_config()

SEARCH_TOLERANCE = 5
SCROLL_STEPS = 3

SHOULD_STOP = False

# ------------------------
# --- Helper Functions ---
# ------------------------


def drag(start: tuple[int, int], end: tuple[int, int], over: float) -> None:
    # moveto and leftclickdown used to drag the screen
    input_controller.moveto(start, TIMES.instant)
    time.sleep(TIMES.action_time)
    input_controller.leftmousedown()
    time.sleep(TIMES.action_time)
    input_controller.moveto(end, over)
    time.sleep(TIMES.action_time)
    input_controller.leftmouseup()
    time.sleep(TIMES.action_time)


def moveto_leftclick(destination: tuple[int, int]) -> None:
    # moveto and leftclick used for buffering actions
    input_controller.moveto(destination, TIMES.instant)
    time.sleep(TIMES.action_time)
    input_controller.leftclick()
    time.sleep(TIMES.action_time)

# ---------------------------
# --- Main Macro Function ---
# ---------------------------


def home_base_actions(loopnum: int) -> None:
    # Navigate to the attack menu
    moveto_leftclick(BUTTON_CONFIG["Attack_Button"])
    moveto_leftclick(BUTTON_CONFIG["Find_Match_Button"])

    activate_window = WINDOW_CONFIG["Activate_Supertroops_Window"]

    # Activate supertroops if necessary
    if "activate" in image_handler.get_str_in_img(activate_window).lower():
        moveto_leftclick(BUTTON_CONFIG["Activate_Supertroops_Button"])
        moveto_leftclick(BUTTON_CONFIG["Activate_Supertroops_Confirm_Button"])

    # Find attack
    moveto_leftclick(BUTTON_CONFIG["Inner_Attack_Button"])

    time.sleep(TIMES.find_attack_time)

    return_home_window = WINDOW_CONFIG["Return_Home_Window"]
    # If return home not found we found a match.
    if "return home" not in image_handler.get_str_in_img(return_home_window).lower():
        return
    else:
        moveto_leftclick(BUTTON_CONFIG["Return_Home_Button"])
        # After N retries kill the program.
        if loopnum >= SEARCH_TOLERANCE:
            raise RecursionError("Could not find a match.")

        home_base_actions(loopnum + 1)


" ADD RESOURCE CHECKING LOGIC HERE"


def attack_base() -> None:
    # Max zoom out for viewing base
    input_controller.scrolldown(SCROLL_STEPS, TIMES.scroll_time)
    time.sleep(TIMES.action_time)

    # Select farming troop
    moveto_leftclick(BUTTON_CONFIG["Troop_Select_Button"])

    # Deploy troops
    drag(MAP_CONFIG["Base_Topleft"], MAP_CONFIG["Base_Maxleft"], Times.troop_drag_time)
    drag(MAP_CONFIG["Base_Topright"], MAP_CONFIG["Base_Maxright"], Times.troop_drag_time)
    drag(MAP_CONFIG["Base_Botleft"], MAP_CONFIG["Base_Maxleft"], Times.troop_drag_time)
    drag(MAP_CONFIG["Base_Botright"], MAP_CONFIG["Base_Maxright"], Times.troop_drag_time)

    damage_window = WINDOW_CONFIG["Damage_Window"]

    timespent = 5
    # Every 5 seconds, check for over 50% destruction, default at 90 seconds total
    while timespent >= 90:
        if image_handler.get_int_in_img(damage_window) >= 50:
            break
        else:
            timespent += 5
            time.sleep(TIMES.destruction_check_time)

    moveto_leftclick(BUTTON_CONFIG["Surrender_Button"])
    moveto_leftclick(BUTTON_CONFIG["Surrender_Okay_Button"])
    moveto_leftclick(BUTTON_CONFIG["Surrender_Return_Home_Button"])


" ADD HOME BASE UPGRADE LOGIC HERE"


def clash_autogrinder(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        # home_base_actions(0)
        attack_base()

# ----------------------
# --- Thread Handler ---
# ----------------------


def main() -> int:
    # Manages the clash thread and the stop thread.
    stop_event = threading.Event()
    worker_thread: threading.Thread | None = None

    # Stops consecutive actions.
    start_hotkey_was_pressed = False
    stop_hotkey_was_pressed = False
    end_hotkey_was_pressed = False
    coords_hotkey_was_pressed = False

    while True:
        start_hotkey_pressed = input_controller.is_hotkey_down(HOTKEYS.start_hotkey)
        stop_hotkey_pressed = input_controller.is_hotkey_down(HOTKEYS.stop_hotkey)
        end_hotkey_pressed = input_controller.is_hotkey_down(HOTKEYS.end_hotkey)
        coords_hotkey_pressed = input_controller.is_hotkey_down(HOTKEYS.coords_hotkey)

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
            # Print to console the coordinates of my cursor.
            print(input_controller.isat())

        start_hotkey_was_pressed = start_hotkey_pressed
        stop_hotkey_was_pressed = stop_hotkey_pressed
        end_hotkey_was_pressed = end_hotkey_pressed
        coords_hotkey_was_pressed = coords_hotkey_pressed

        time.sleep(TIMES.hotkey_poll)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
