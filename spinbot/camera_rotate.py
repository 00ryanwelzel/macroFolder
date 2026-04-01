import ctypes
import threading
import time

# windows bs
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
VK_END = 0x23

# y osc
OSC_RANGE = 100
OSC_STEP = 5


ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION),
    ]


def oscillator(height: int, step: int) -> int:
    cycle = max(1, 2 * height)
    position = step % cycle
    if position > height:
        return cycle - position
    return position


def move_mouse_relative(dx: int, dy: int) -> None:
    extra = ctypes.c_ulong(0)
    mouse_input = MOUSEINPUT(
        dx=dx,
        dy=dy,
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE,
        time=0,
        dwExtraInfo=ctypes.pointer(extra),
    )
    command = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mouse_input))
    ctypes.windll.user32.SendInput(1, ctypes.byref(command), ctypes.sizeof(INPUT))


def watch_for_stop(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        if ctypes.windll.user32.GetAsyncKeyState(VK_END) & 0x8000:
            stop_event.set()
            return
        time.sleep(0.05)


def main() -> None:
    step_pixels = 10
    interval_seconds = 0.03

    stop_event = threading.Event()
    watcher = threading.Thread(target=watch_for_stop, args=(stop_event,), daemon=True)
    watcher.start()

    print("Starting horizontal camera rotation in 5.")
    print("Press END to stop.")

    time.sleep(5)

    try:
        i = 0
        previous_y = oscillator(OSC_RANGE, 0)
        while not stop_event.is_set():
            i += OSC_STEP
            current_y = oscillator(OSC_RANGE, i)
            move_mouse_relative(step_pixels, current_y - previous_y)
            previous_y = current_y
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        print("Rotation stopped.")

    return


if __name__ == "__main__":
    main()
