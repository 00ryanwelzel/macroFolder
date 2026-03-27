from dataclasses import dataclass, fields
from math import floor
import threading

import keyboard
import time
import sys
import pyautogui

' window measurements for initial coordinates '
INITIAL_TL_COORDS = 18, 222
INITIAL_BR_COORDS = 923, 802

CURRENT_TL_COORDS = 9, 194
CURRENT_BR_COORDS = 864, 711

STOP_EVENT = threading.Event()

SHOULD_STOP = False

@dataclass
class Coordinates:
    MITHRIL: tuple = (435, 400)
    COAL: tuple = (400, 400)
    ORDERS: tuple = (505, 540)
    BUY_ORDER: tuple = (545, 435)
    AMOUNT: tuple = (580, 435)
    DONE: tuple = (470, 700)
    TOP_ORDER: tuple = (435, 435)
    PLACE_ORDER: tuple = (470, 435)
    COLLECT_ORDER: tuple = (365, 470)
    CANCEL_ORDER: tuple = (400, 435)
    SELL: tuple = (400, 540)
    CONFIRM_SELL: tuple = (400, 450)

@dataclass
class Commands:
    JOIN_SKYBLOCK = "/skyblock"
    BZ_ENTER = "/bz"
    BZ_MITHRIL = "/bz mithril"
    BZ_COAL = "/bz coal"
    BZ_MAX_PURCHASE = "71680"

@dataclass
class Hotkeys:
    START_HOTKEY = 'ctrl', 'alt', '1'
    STOP_HOTKEY = 'ctrl', 'alt', '2'
    TEST_HOTKEY = 'ctrl', 'alt', '3'
    SET_TL_HOTKEY = 'ctrl', 'alt', '4'
    SET_BR_HOTKEY = 'ctrl', 'alt', '5'
    KILL_HOTKEY = 'ctrl', 'alt', '0'

@dataclass
class SleepTimes:
    POLL_SLEEP = 0.2
    KEYBOARD_SLEEP = 0.1
    ORDER_SLEEP = 45
    ACTION_SLEEP = 0.6
    COLLECTION_SLEEP = 0.5
    REJOIN_SLEEP = 4


# - helpers -

def scale_coordinates():
    for c in fields(Coordinates):
        x, y = getattr(Coordinates, c.name)

        c0 = floor(x * CURRENT_BR_COORDS[0] / INITIAL_BR_COORDS[0])
        c0 = c0 + CURRENT_TL_COORDS[0] - INITIAL_TL_COORDS[0]

        c1 = floor(y * CURRENT_BR_COORDS[1] / INITIAL_BR_COORDS[1])
        c1 = c1 + CURRENT_TL_COORDS[1] - INITIAL_TL_COORDS[1]

        setattr(Coordinates, c.name, (c0, c1))

    return


def check_hotkey(hotkey):
    for k in hotkey:
        if not keyboard.is_pressed(k): return False

    return True


def execute_command(command):
    for c in command:
        if SHOULD_STOP: return

        pyautogui.press(c)
        pyautogui.sleep(SleepTimes.KEYBOARD_SLEEP)

    pyautogui.press('enter')
    pyautogui.sleep(SleepTimes.ACTION_SLEEP)

    return

def execute_sequence(sequence):
    for s in sequence:
        if SHOULD_STOP: return

        pyautogui.moveTo(s)
        pyautogui.sleep(SleepTimes.ACTION_SLEEP)

        pyautogui.click(s)
        pyautogui.sleep(SleepTimes.ACTION_SLEEP)

    return


# - macro segments -

def create_order(material):
    if SHOULD_STOP: return

    match material:
        case "mithril":
            material_coordinates = Coordinates.MITHRIL
            material_command = Commands.BZ_MITHRIL

        case "coal":
            material_coordinates = Coordinates.COAL
            material_command = Commands.BZ_COAL

        case _:
            print(f"Material [{material}] does not exist.")
            return

    start_sequence = [
        material_coordinates,
        Coordinates.BUY_ORDER,
        Coordinates.AMOUNT
    ]

    end_sequence = [
        Coordinates.DONE,
        Coordinates.TOP_ORDER,
        Coordinates.PLACE_ORDER
    ]

    execute_command(material_command)
    execute_sequence(start_sequence)
    execute_command(Commands.BZ_MAX_PURCHASE)
    execute_sequence(end_sequence)

    return


def collect_order():
    if SHOULD_STOP: return

    sequence = [
        Coordinates.ORDERS,
        Coordinates.COLLECT_ORDER
    ]

    execute_command(Commands.BZ_ENTER)
    execute_sequence(sequence)

    for i in range(0, 45):
        if SHOULD_STOP: return

        pyautogui.click(Coordinates.COLLECT_ORDER)
        pyautogui.sleep(SleepTimes.COLLECTION_SLEEP)

    pyautogui.press('esc')
    pyautogui.sleep(SleepTimes.ACTION_SLEEP)

    return


def cancel_order():
    if SHOULD_STOP: return

    sequence = [
        Coordinates.ORDERS,
        Coordinates.COLLECT_ORDER,
        Coordinates.CANCEL_ORDER
    ]

    execute_command(Commands.BZ_ENTER)
    execute_sequence(sequence)

    pyautogui.press('esc')
    pyautogui.sleep(SleepTimes.ACTION_SLEEP)

    return


def sell_inventory():
    if SHOULD_STOP: return

    sequence = [
        Coordinates.SELL,
        Coordinates.CONFIRM_SELL
    ]

    execute_command(Commands.BZ_ENTER)
    execute_sequence(sequence)

    pyautogui.press('esc')
    pyautogui.sleep(SleepTimes.ACTION_SLEEP)

    return

# - core functionality -

def main():
    while not STOP_EVENT.is_set():
        execute_command(Commands.JOIN_SKYBLOCK)

        pyautogui.sleep(SleepTimes.REJOIN_SLEEP)

        create_order("coal")
        create_order("mithril")

        pyautogui.sleep(SleepTimes.ORDER_SLEEP)

        for i in range(0, 5):
            execute_command(Commands.JOIN_SKYBLOCK)

            pyautogui.sleep(SleepTimes.REJOIN_SLEEP)

            collect_order()
            cancel_order()

        sell_inventory()

    return

# - testers -

def test_scale_fn():
    print("Displaying scaled coordinates:")

    for c in fields(Coordinates):
        print(getattr(Coordinates, c.name))

    return

# - controller -

if __name__ == "__main__":
    t = None

    while True:
        if check_hotkey(Hotkeys.KILL_HOTKEY) and (t is None):
            sys.exit(0)

        if check_hotkey(Hotkeys.START_HOTKEY) and (t is None):
            SHOULD_STOP = False
            STOP_EVENT.clear()
            print("Waiting to start macro...")
            pyautogui.sleep(2)
            t = threading.Thread(target=main, daemon=True)
            t.start()
            print(f"Macro t_id[{t.ident}] started")

        if check_hotkey(Hotkeys.STOP_HOTKEY) and (t is not None):
            print(f"Macro t_id[{t.ident}] stopped")
            SHOULD_STOP = True
            STOP_EVENT.set()
            t = None

        if check_hotkey(Hotkeys.TEST_HOTKEY):
            print("Waiting to start cursor display...")
            pyautogui.sleep(2)
            while not check_hotkey(Hotkeys.TEST_HOTKEY):
                pyautogui.sleep(SleepTimes.KEYBOARD_SLEEP)
                print(f"Cursor at {pyautogui.position()}")

        if check_hotkey(Hotkeys.SET_TL_HOTKEY):
            pyautogui.moveTo(INITIAL_TL_COORDS)

        if check_hotkey(Hotkeys.SET_BR_HOTKEY):
            pyautogui.moveTo(INITIAL_BR_COORDS)

        time.sleep(SleepTimes.POLL_SLEEP)