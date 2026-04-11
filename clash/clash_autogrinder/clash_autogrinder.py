import threading
import time

import image_handler
import input_handler
import config_handler
from constants import WaitTimes, ResourceMinimums

BUTTON_CONFIG = config_handler.load_button_config()
WINDOW_CONFIG = config_handler.load_window_config()
MAP_CONFIG = config_handler.load_map_config()

ATTACK_SEARCH_LIMIT = 5
SCROLL_OUT_STEPS = 3

# --- Helpers ---


def drag(start: tuple[int, int], end: tuple[int, int], over: float) -> None:
    input_handler.moveto(start)
    input_handler.leftmousedown()
    input_handler.moveto(end, over)
    input_handler.leftmouseup()


def moveto_leftclick(destination: tuple[int, int]) -> None:
    input_handler.moveto(destination)
    input_handler.leftclick()

# --- Main Logic ---


def find_match() -> bool:
    moveto_leftclick(BUTTON_CONFIG["Attack_Button"])
    moveto_leftclick(BUTTON_CONFIG["Find_Match_Button"])

    activate_window = WINDOW_CONFIG["Activate_Supertroops_Window"]

    if "activate" in image_handler.get_str_in_img(activate_window).lower():
        moveto_leftclick(BUTTON_CONFIG["Activate_Supertroops_Button"])
        moveto_leftclick(BUTTON_CONFIG["Activate_Supertroops_Confirm_Button"])

    moveto_leftclick(BUTTON_CONFIG["Inner_Attack_Button"])

    return not abort_find_match()


def abort_find_match() -> bool:
    # Checks for a stuck loading screen, indicated by a return button existing.
    time.sleep(WaitTimes.loading)

    return_home_window = WINDOW_CONFIG["Return_Home_Window"]

    if "return home" not in image_handler.get_str_in_img(return_home_window).lower():
        return False

    moveto_leftclick(BUTTON_CONFIG["Return_Home_Button"])
    time.sleep(WaitTimes.loading)
    return True


def check_base_resources() -> bool:
    # Skip bases that have too little resources.
    gold_window = WINDOW_CONFIG["Enemy_Gold_Window"]
    elixir_window = WINDOW_CONFIG["Enemy_Elixir_Window"]
    dark_window = WINDOW_CONFIG["Enemy_Dark_Window"]

    if ResourceMinimums.gold > image_handler.get_int_in_img(gold_window):
        moveto_leftclick(BUTTON_CONFIG["Next_Button"])
        return not abort_find_match()

    if ResourceMinimums.elixir > image_handler.get_int_in_img(elixir_window):
        moveto_leftclick(BUTTON_CONFIG["Next_Button"])
        return not abort_find_match()

    if ResourceMinimums.dark > image_handler.get_int_in_img(dark_window):
        moveto_leftclick(BUTTON_CONFIG["Next_Button"])
        return not abort_find_match()

    return True


def attack_base() -> None:
    # Deploys troops, waits for either 50% destruction or 90 seconds to abort.
    input_handler.scrolldown(SCROLL_OUT_STEPS, WaitTimes.scroll)

    moveto_leftclick(BUTTON_CONFIG["Troop_Select_Button"])

    drag(MAP_CONFIG["Base_Topleft"], MAP_CONFIG["Base_Maxleft"], WaitTimes.troop_drag)
    drag(MAP_CONFIG["Base_Topright"], MAP_CONFIG["Base_Maxright"], WaitTimes.troop_drag)
    drag(MAP_CONFIG["Base_Botleft"], MAP_CONFIG["Base_Maxleft"], WaitTimes.troop_drag)
    drag(MAP_CONFIG["Base_Botright"], MAP_CONFIG["Base_Maxright"], WaitTimes.troop_drag)

    damage_window = WINDOW_CONFIG["Damage_Window"]

    timespent = WaitTimes.destruction_check
    while timespent < 90:
        if image_handler.get_int_in_img(damage_window) >= 50:
            break

        timespent += WaitTimes.destruction_check
        time.sleep(WaitTimes.destruction_check)

    moveto_leftclick(BUTTON_CONFIG["Surrender_Button"])
    moveto_leftclick(BUTTON_CONFIG["Surrender_Okay_Button"])
    moveto_leftclick(BUTTON_CONFIG["Surrender_Return_Home_Button"])


def get_upgrade_prices() -> None:
    pass


def clash_autogrinder(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        get_upgrade_prices()

        for _ in range(ATTACK_SEARCH_LIMIT):
            if stop_event.is_set():
                return

            if not find_match():
                continue

            if not check_base_resources():
                continue

            # attack_base()
            break
        else:
            raise RecursionError("Could not find an attackable base.")

        attack_base()
        break
