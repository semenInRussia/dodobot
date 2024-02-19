import pyautogui as _pg
from numpy import select

from gamer import DURATION


def click(
    x: int | tuple[int, int] | None = None, y: int = 0, duration: float = 0
) -> None:
    p: tuple[int, int] | None = None
    if type(x) == tuple:
        p = x
    elif type(x) == int:
        p = (x, y)

    if p is not None:
        move(p)

    _pg.click(duration=duration)


mouse_up = _pg.mouseUp
mouse_down = _pg.mouseDown


def move(x: int | tuple[int, int], y: int | None = None, duration: float = 0) -> None:
    if (
        (type(x) == int or type(y) == int)
        and type(y) != type(x)
        or (type(x) != int and type(x) != tuple)
    ):
        raise TypeError("expected either int and int or tuple of 2 integers")

    p: tuple[int, int] = (0, 0)

    if type(x) == tuple:
        p = x
    elif type(x) == int and type(y) == int:
        p = x, y

    x, y = p
    _pg.moveTo(x, y, duration=duration)
