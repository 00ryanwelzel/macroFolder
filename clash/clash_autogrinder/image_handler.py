import re
import pytesseract
from pathlib import Path
from PIL import Image, ImageGrab, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESSERACT_EXE = PROJECT_ROOT / "Tesseract-OCR" / "tesseract.exe"

if TESSERACT_EXE.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)
else:
    raise FileNotFoundError(f"Tesseract not found at {TESSERACT_EXE}")

# ---------------
# --- Helpers ---
# ---------------


def capture_region(topleft: tuple[int, int], botright: tuple[int, int]) -> Image.Image:
    # Get the image displayed within a defined region.
    left, top = topleft
    right, bottom = botright

    if right <= left or bottom <= top:
        raise ValueError("botright values must be strictly greater than topleft")

    return ImageGrab.grab(bbox=(left, top, right, bottom))


def prepare_for_ocr(image: Image.Image) -> Image.Image:
    grayscale = ImageOps.grayscale(image)
    enlarged = grayscale.resize((grayscale.width * 2, grayscale.height * 2))
    return ImageOps.autocontrast(enlarged)


def read_text(image: Image.Image, config: str = "") -> str:
    raw_text = pytesseract.image_to_string(prepare_for_ocr(image), config=config)
    return raw_text.strip()

# ----------------------
# --- Main Functions ---
# ----------------------


def get_str_in_img(topleft: tuple[int, int], botright: tuple[int, int]) -> list[str] | str:
    # Finds and returns every string in an image.
    image = capture_region(topleft, botright)
    text = read_text(image)
    strings = [line.strip() for line in text.splitlines() if line.strip()]

    if len(strings) == 1:
        return strings[0]

    return strings


def get_int_in_img(topleft: tuple[int, int], botright: tuple[int, int]) -> list[int] | int:
    # Finds and returns every integer in an image.
    image = capture_region(topleft, botright)
    text = read_text(image, config="--psm 6")
    integers = [int(match) for match in re.findall(r"-?\d+", text)]

    if len(integers) == 1:
        return integers[0]

    return integers
