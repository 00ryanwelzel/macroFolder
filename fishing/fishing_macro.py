from dataclasses import dataclass, fields
from math import floor
import threading
import keyboard
import time
import sys
import os
import pyautogui
from PIL import Image

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

INDICATOR_COORDS_X, INDICATOR_COORDS_Y = 280, 890
LOCATION_COORDS_X, LOCATION_COORDS_Y = 520, 383

CURRENT_CURSOR_X, CURRENT_CURSOR_Y = 0, 0

SHORT_BUFFER = 0.2

# - images
FISHING_INDICATOR = "fishing_catch_indicator.png"

# - operations keys
START_KEY = '0'
STOP_KEY = '2'
DEBUG_COORDINATES_KEY = '3'
SET_COORDINATES_KEY = '4'

# - game keys
FISHING_ROD_KEY = '3'
FIRE_VEIL_KEY = '4'

STOP_EVENT = threading.Event()

# - rod caught scan area
INDICATOR_REGION_W = 120
INDICATOR_REGION_H = 120

# - at hub base area
SERVER_REGION_W = 85
SERVER_REGION_H = 85

# - confidence intervals
INDICATOR_CONFIDENCE = 0.34
SERVER_CONFIDENCE = 0.2
MASK_MATCH_THRESHOLD = 0.45
MIN_MASK_PIXELS = 125

POLL_INTERVAL = 0.05
DOUBLE_CLICK_GAP = 0.05
DEBOUNCE = 0.25


def loadAndFit(path: str, max_w: int, max_h: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size

    if w <= max_w and h <= max_h:
        return img

    img_copy = img.copy()
    img_copy.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return img_copy

def pilToCv(image: Image.Image):
    return cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)

def buildIndicatorMask(image: Image.Image):
    bgr_img = pilToCv(image)
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # The indicator is dominated by saturated red tones. Building a mask
    # for those colors makes matching much less sensitive to the background.
    lower_red_1 = np.array([0, 70, 45], dtype=np.uint8)
    upper_red_1 = np.array([15, 255, 255], dtype=np.uint8)
    lower_red_2 = np.array([170, 70, 45], dtype=np.uint8)
    upper_red_2 = np.array([179, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv_img, lower_red_1, upper_red_1)
    mask |= cv2.inRange(hsv_img, lower_red_2, upper_red_2)

    kernel = np.ones((3, 3), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def cropMaskToContent(mask):
    points = cv2.findNonZero(mask)
    if points is None:
        return mask

    x, y, w, h = cv2.boundingRect(points)
    return mask[y:y + h, x:x + w]

def indicatorPresent(region, template_mask) -> bool:
    screenshot = pyautogui.screenshot(region=region)
    screenshot_bgr = pilToCv(screenshot)
    screenshot_hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)

    lower_red_1 = np.array([0, 70, 45], dtype=np.uint8)
    upper_red_1 = np.array([15, 255, 255], dtype=np.uint8)
    lower_red_2 = np.array([170, 70, 45], dtype=np.uint8)
    upper_red_2 = np.array([179, 255, 255], dtype=np.uint8)

    screen_mask = cv2.inRange(screenshot_hsv, lower_red_1, upper_red_1)
    screen_mask |= cv2.inRange(screenshot_hsv, lower_red_2, upper_red_2)

    kernel = np.ones((3, 3), dtype=np.uint8)
    screen_mask = cv2.morphologyEx(screen_mask, cv2.MORPH_OPEN, kernel)
    screen_mask = cv2.morphologyEx(screen_mask, cv2.MORPH_CLOSE, kernel)

    result = cv2.matchTemplate(screen_mask, template_mask, cv2.TM_CCORR_NORMED)
    _, max_score, _, _ = cv2.minMaxLoc(result)
    return max_score >= MASK_MATCH_THRESHOLD

def main():
    CURRENT_CURSOR_X, CURRENT_CURSOR_Y = pyautogui.position()

    # initial
    pyautogui.press(FISHING_ROD_KEY)
    pyautogui.rightClick(CURRENT_CURSOR_X, CURRENT_CURSOR_Y)

    indicator_region = (INDICATOR_COORDS_X, INDICATOR_COORDS_Y, INDICATOR_REGION_W, INDICATOR_REGION_H)
    
    # path to script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # image scraping comparators path
    indicator_path = os.path.join(script_dir, FISHING_INDICATOR)
    if not os.path.exists(indicator_path):
        print(f"Indicator image not found at: {indicator_path}")
        return

    indicator_img = loadAndFit(
        indicator_path,
        INDICATOR_REGION_W,
        INDICATOR_REGION_H
    )

    use_mask_matching = cv2 is not None and np is not None
    indicator_mask = None
    if use_mask_matching:
        indicator_mask = cropMaskToContent(buildIndicatorMask(indicator_img))
        if cv2.countNonZero(indicator_mask) < MIN_MASK_PIXELS:
            use_mask_matching = False
            print("Indicator mask too sparse, falling back to locateOnScreen")
        else:
            print("Using masked indicator matching")
    else:
        print("OpenCV/numpy not available, falling back to locateOnScreen")

    FAILED_POLLS = 0

    while not STOP_EVENT.is_set():
        if use_mask_matching:
            indicator_found = indicatorPresent(indicator_region, indicator_mask)
            if not indicator_found:
                FAILED_POLLS += 1
        else:
            try:
                indicator_found = pyautogui.locateOnScreen(
                    indicator_img,
                    region=indicator_region,
                    confidence=INDICATOR_CONFIDENCE
                )
            except pyautogui.ImageNotFoundException:
                indicator_found = None
                FAILED_POLLS += 1

        if indicator_found or FAILED_POLLS >= 500:
            pyautogui.rightClick(CURRENT_CURSOR_X, CURRENT_CURSOR_Y)
            time.sleep(DOUBLE_CLICK_GAP)
            pyautogui.press(FIRE_VEIL_KEY)
            time.sleep(DOUBLE_CLICK_GAP)
            pyautogui.rightClick(CURRENT_CURSOR_X, CURRENT_CURSOR_Y)
            time.sleep(DOUBLE_CLICK_GAP)
            pyautogui.press(FISHING_ROD_KEY)
            time.sleep(DOUBLE_CLICK_GAP)
            pyautogui.rightClick(CURRENT_CURSOR_X, CURRENT_CURSOR_Y)

            FAILED_POLLS = 0

            time.sleep(DEBOUNCE)

        else:
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    t = None

    while True:
        if keyboard.is_pressed(START_KEY) and (t is None or not t.is_alive()):
            STOP_EVENT.clear()
            t = threading.Thread(target=main, daemon=True)
            t.start()

        if keyboard.is_pressed(STOP_KEY):
            STOP_EVENT.set()
            print("stopped")

        if keyboard.is_pressed(DEBUG_COORDINATES_KEY):
            print(pyautogui.position())

        if keyboard.is_pressed(SET_COORDINATES_KEY):
            print(f"Setting scan base coords to {pyautogui.position()}")
            INDICATOR_COORDS_X, INDICATOR_COORDS_Y = pyautogui.position()

        time.sleep(SHORT_BUFFER)

    sys.exit(0)
