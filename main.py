from dataclasses import dataclass, fields
from math import floor
import threading
import keyboard
import time
import sys
import pyautogui


REFERENCE_OFFSET_X, REFERENCE_OFFSET_Y = 9, 3
''' VVV - CHANGE THIS - VVV '''
REAL_OFFSET_X, REAL_OFFSET_Y = 296, 163

REFERENCE_RES_X, REFERENCE_RES_Y = 800, 600
''' VVV - CHANGE THIS - VVV '''
REAL_RES_X, REAL_RES_Y = 800, 600

SHORT_BUFFER = 0.5
MED_BUFFER = 2.5
LONG_BUFFER = 5
DEFLATION_RUNTIME = 350

START_KEY = '1'
STOP_KEY = '2'
COORDINATES_KEY = '3'
FLEX_TEST_KEY = '4'

STOP_EVENT = threading.Event()


@dataclass
class Select:
    HERO: tuple = (185, 590)
    ALCH: tuple = (300, 590)
    MERM: tuple = (405, 590)
    SPIKE: tuple = (470, 590)
    VILLAGE: tuple = (525, 590)

@dataclass
class Place:
    HERO: tuple = (390, 205)
    ALCH: tuple = (440, 210)
    MERM: tuple = (425, 250)
    SPIKE: tuple = (480, 250)
    VILLAGE: tuple = (490, 200)

@dataclass
class Path:
    TOP: tuple = (160, 300)
    MID: tuple = (160, 380)
    BOT: tuple = (160, 460)

@dataclass
class Drag:
    RIGHT: tuple = (630, 590)
    LEFT: tuple = (185, 590)

@dataclass
class Buttons:
    PLAY: tuple = (415, 585)
    EXPERT: tuple = (600, 585)
    DARK_CASTLE: tuple = (415, 350)

    EASY: tuple = (245, 275)
    DEFLATION: tuple = (565, 300)
    PLAY_DEFLATION: tuple = (410, 450)

    SPEED_TOGGLE: tuple = (765, 595)
    LEVEL_UP_CONFIRM: tuple = (515, 430)

    CLOSE_ENDSCREEN: tuple = (415, 530)
    HOME: tuple = (290, 500)

    LEFT_TOWER: tuple = (330, 340)
    RIGHT_TOWER: tuple = (480, 340)
    CLOSE_COLLECTION: tuple = (45, 65)

select = Select()
place = Place()
path = Path()
drag = Drag()
buttons = Buttons()

ALL_OBJECTS = [select, place, path, drag, buttons]


# - utility

def adjust_coordinates(x, y):
    scaled_x = floor(x * REAL_RES_X / REFERENCE_RES_X)
    scaled_x = scaled_x + REAL_OFFSET_X - REFERENCE_OFFSET_X
    scaled_y = floor(y * REAL_RES_Y / REFERENCE_RES_Y)
    scaled_y = scaled_y + REAL_OFFSET_Y - REFERENCE_OFFSET_Y
    return scaled_x, scaled_y


def scale_all_coordinates():
    for obj in ALL_OBJECTS:
        for f in fields(obj):
            x, y = getattr(obj, f.name)
            setattr(obj, f.name, adjust_coordinates(x, y))


def safe_sleep(seconds):
    end = time.time() + seconds
    while time.time() < end:
        if STOP_EVENT.is_set():
            return False
        time.sleep(0.05)
    return True


# - actions

def place_and_select(menu_pos, map_pos):
    if not safe_sleep(SHORT_BUFFER): return
    pyautogui.click(*menu_pos)
    if not safe_sleep(SHORT_BUFFER): return
    pyautogui.click(*map_pos)
    if not safe_sleep(SHORT_BUFFER): return
    pyautogui.click(*map_pos)

def upgrade_path(top, mid, bot):
    for _ in range(top):
        if STOP_EVENT.is_set(): return
        pyautogui.click(*path.TOP)
        safe_sleep(SHORT_BUFFER)

    for _ in range(mid):
        if STOP_EVENT.is_set(): return
        pyautogui.click(*path.MID)
        safe_sleep(SHORT_BUFFER)

    for _ in range(bot):
        if STOP_EVENT.is_set(): return
        pyautogui.click(*path.BOT)
        safe_sleep(SHORT_BUFFER)


def drag_bar(start, end):
    if not safe_sleep(SHORT_BUFFER): return
    pyautogui.mouseDown(x=start[0], y=start[1])
    pyautogui.moveTo(end[0], end[1], duration=MED_BUFFER)
    pyautogui.mouseUp()


# - sequence functions

def place_towers():
    place_and_select(select.HERO, place.HERO)

    drag_bar(drag.RIGHT, drag.LEFT)
    drag_bar(drag.RIGHT, drag.LEFT)

    place_and_select(select.ALCH, place.ALCH)
    upgrade_path(3, 2, 0)

    place_and_select(select.MERM, place.MERM)
    upgrade_path(4, 0, 2)

    place_and_select(select.SPIKE, place.SPIKE)
    upgrade_path(1, 0, 4)

    place_and_select(select.VILLAGE, place.VILLAGE)
    upgrade_path(2, 2, 0)


def close_collection_event_menu():
    sequence = [
        buttons.LEFT_TOWER,
        buttons.LEFT_TOWER,
        buttons.LEFT_TOWER,
        buttons.LEFT_TOWER,
        buttons.RIGHT_TOWER,
        buttons.RIGHT_TOWER,
        buttons.RIGHT_TOWER,
        buttons.RIGHT_TOWER,
        buttons.CLOSE_COLLECTION
    ]

    for pos in sequence:
        if STOP_EVENT.is_set(): return
        safe_sleep(MED_BUFFER)
        pyautogui.click(*pos)


def start_deflation():
    sequence = [
        buttons.PLAY,
        buttons.EXPERT,
        buttons.EXPERT,
        buttons.DARK_CASTLE,
        buttons.EASY,
        buttons.DEFLATION
    ]

    for pos in sequence:
        if STOP_EVENT.is_set(): return
        safe_sleep(SHORT_BUFFER)
        pyautogui.click(*pos)

    safe_sleep(LONG_BUFFER)
    pyautogui.click(*buttons.PLAY_DEFLATION)


# - all of it

def main():
    scale_all_coordinates()

    while not STOP_EVENT.is_set():
        start_deflation()
        safe_sleep(SHORT_BUFFER)

        place_towers()

        safe_sleep(SHORT_BUFFER)
        pyautogui.click(*buttons.SPEED_TOGGLE)
        safe_sleep(SHORT_BUFFER)
        pyautogui.click(*buttons.SPEED_TOGGLE)

        start_time = time.time()
        while time.time() - start_time < DEFLATION_RUNTIME:
            if STOP_EVENT.is_set():
                return
            safe_sleep(MED_BUFFER)
            pyautogui.click(*buttons.LEVEL_UP_CONFIRM)
            safe_sleep(MED_BUFFER)
            pyautogui.click(*buttons.LEVEL_UP_CONFIRM)

        safe_sleep(SHORT_BUFFER)
        pyautogui.click(*buttons.CLOSE_ENDSCREEN)
        safe_sleep(SHORT_BUFFER)
        pyautogui.click(*buttons.HOME)

        safe_sleep(LONG_BUFFER)
        close_collection_event_menu()


# - start

if __name__ == "__main__":
    t = None

    while True:
        if keyboard.is_pressed(START_KEY) and (t is None or not t.is_alive()):
            STOP_EVENT.clear()
            t = threading.Thread(target=main, daemon=True)
            t.start()

        if keyboard.is_pressed(STOP_KEY):
            STOP_EVENT.set()
            break

        if keyboard.is_pressed(COORDINATES_KEY):
            print(pyautogui.position())

        if keyboard.is_pressed(FLEX_TEST_KEY):
            scale_all_coordinates()
            close_collection_event_menu()
            print("test")

        time.sleep(0.2)

    sys.exit(0)