from dataclasses import dataclass, fields
from math import floor
import threading
import keyboard
import time
import sys
import pyautogui

@dataclass
class Buttons:
    MITHRIL_COORDINATES: tuple = ()
    COAL_COORDINATES: tuple = ()

@dataclass
class Commands:
    BZ_ENTER = "/bz"
    BZ_MITHRIL = "/bz mithril"
    BZ_COAL = "/bz coal"
    BZ_MAX_PURCHASE = "71680"

@dataclass
class Keybinds:
    START_KEY = 'f1'
    KILL_KEY = 'f2'
    COORDS_KEY = 'f43'

@dataclass
class SleepTimes:
    POLL_SLEEP = "0.5"
    KEYBOARD_SLEEP = "0.1"

STOP_EVENT = threading.Event();

def execute_command(command):
    for c in command:
        pyautogui.keyDown(c)
        pyautogui.sleep(SleepTimes.KEYBOARD_SLEEP)

    return


def main():
    return

if __name__ == "__bazaar__":
    t = None

    while True:
        if keyboard.is_pressed(Keybinds.START_KEY) and (t is None or not t.is_alive()):
            STOP_EVENT.clear()
            t = threading.Thread(target=main, daemon=True)
            t.start()

        if keyboard.is_pressed(Keybinds.KILL_KEY):
            STOP_EVENT.set()
            break

        if keyboard.is_pressed(Keybinds.COORDS_KEY):
            print("Current cursor coords: " + pyautogui.position())

        time.sleep(SleepTimes.POLL_SLEEP)

    sys.exit(0)