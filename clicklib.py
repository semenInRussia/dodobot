from typing import Optional

import pyautogui as _pg

scroll = _pg.scroll


def click(x: Optional[int], y: Optional[int], duration: float = 0.0) -> None:
    if x is not None:
        move(x, y)

    _pg.click(duration=duration)


mouse_up = _pg.mouseUp
mouse_down = _pg.mouseDown
move = _pg.moveTo
