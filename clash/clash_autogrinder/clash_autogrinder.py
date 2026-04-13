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

UPGRADE_MENU: dict[tuple[str, int], int] = {}

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
    # Rebuild the menu from the currently open builder list.
    UPGRADE_MENU.clear()
    previous_final_upgrade = None

    while True:
        # Read the currently visible builder rows from separate name and price windows.
        raw_names = image_handler.get_str_in_img(WINDOW_CONFIG["Builder_Name_Window"])
        raw_prices = image_handler.get_int_in_img(WINDOW_CONFIG["Builder_Price_Window"])

        def parse_upgrade(in_name: str, in_price: int) -> tuple[tuple[str, int], int]:
            # Count text comes before the first letter; the rest is the upgrade name.
            count_string = ""
            name_start_index = 0
            for index, character in enumerate(in_name):
                if character.isalpha():
                    name_start_index = index
                    break

                count_string += character

            count_string = count_string.strip()
            count = int(count_string) if count_string else 1
            in_name = in_name[name_start_index:].strip()
            return (in_name, count), in_price

        if names_length == 0:
            break

        # If the final visible row does not change after dragging, the menu has stopped scrolling.
        if isinstance(raw_names, str):
            final_name = raw_names
        else:
            final_name = raw_names[-1]

        if isinstance(raw_prices, int):
            final_price = raw_prices
        else:
            final_price = raw_prices[-1]

        current_final_upgrade = parse_upgrade(final_name, final_price)

        if current_final_upgrade == previous_final_upgrade:
            break

        # Store directly into the declared menu dict as (name, count) -> price.
        if isinstance(raw_names, str):
            price = raw_prices if isinstance(raw_prices, int) else raw_prices[0]
            upgrade, price = parse_upgrade(raw_names, price)
            UPGRADE_MENU[upgrade] = price
        elif isinstance(raw_prices, int):
            upgrade, price = parse_upgrade(raw_names[0], raw_prices)
            UPGRADE_MENU[upgrade] = price
        else:
            for name, price in zip(raw_names, raw_prices):
                # Names and prices are paired by matching index; leading count text is stored separately.
                upgrade, price = parse_upgrade(name, price)
                UPGRADE_MENU[upgrade] = price

        previous_final_upgrade = current_final_upgrade
        drag(MAP_CONFIG["Builder_Menu_Scroll_Bottom"], MAP_CONFIG["Builder_Menu_Scroll_Top"], WaitTimes.scroll)


def prices_tester() -> None:
    moveto_leftclick(BUTTON_CONFIG["Builder_Button"])
    get_upgrade_prices()


def clash_autogrinder(stop_event: threading.Event) -> None:
    """
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
        """
