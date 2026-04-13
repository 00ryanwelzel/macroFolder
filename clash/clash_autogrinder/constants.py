from dataclasses import dataclass


@dataclass(frozen=True)
class WaitTimes:
    instant: float = 0.01
    end_of_action: float = 0.5
    loading: float = 3.5
    scroll: float = 1
    troop_drag: float = 7
    destruction_check: float = 5


@dataclass(frozen=True)
class PollTimes:
    user_poll: float = 0.10
    hotkey_poll: float = 0.05


@dataclass(frozen=True)
class Hotkeys:
    start_hotkey: tuple[str, ...] = ("ctrl", "alt", "1")
    stop_hotkey: tuple[str, ...] = ("ctrl", "alt", "2")
    end_hotkey: tuple[str, ...] = ("ctrl", "alt", "3")
    coords_hotkey: tuple[str, ...] = ("ctrl", "alt", "4")
    test_hotkey: tuple[str, ...] = ("ctrl", "alt", "5")


@dataclass(frozen=True)
class ResourceMinimums:
    gold: int = 0
    elixir: int = 0
    dark: int = 0
