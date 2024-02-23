import time
from typing import Literal

import pyautogui as pg
from PIL import Image

import clicklib
import photo
import regimg
from photo import Rect, extract_table_image
from screener import screen
from tsrct import extract_table
from worder import WordPath, n, random_5letters_words, search, sync_words_with_dict

DURATION = 0.2
EVENTS_SLEEP_TIME = 1

rus_keyboard = "йцукенгшщзхъфывапролджэячсмитьбю"
eng_keyboard = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
_rus_to_eng = dict(zip(rus_keyboard, eng_keyboard))

event = (
    Literal["credits"]
    | Literal["disconnect"]
    | Literal["home"]
    | Literal["playing"]
    | Literal["round1help1"]
    | Literal["round1help2"]
    | Literal["roundend"]
    | Literal["start"]
    | Literal["who"]
    | Literal["winner"]
    | Literal["wordchoose"]
)


def _is_good_start_word(w: str) -> bool:
    return "ь" not in w and "ё" not in w


_wrds = filter(_is_good_start_word, random_5letters_words)


def _press_rus_char(ch: str) -> None:
    pg.press(_rus_to_eng.get(ch, ""))


class Gamer:
    _table: list[str] | None = None
    _table_box: Rect | None = None
    _screen: Image.Image | None = None
    _prev_event: str | None

    def __init__(self):
        self.reset()
        clicklib.click()
        clicklib.scroll(10)
        clicklib.scroll(-1)

    def start(self):
        prev_is_playing = False
        while True:
            time.sleep(EVENTS_SLEEP_TIME)
            p = regimg.predict(screen())
            if prev_is_playing and p.name == "playing":
                # don't play twice at the same round
                continue
            prev_is_playing = p.name == "playing"
            self._handle_regimg(p)

    def step(self) -> None:
        p = regimg.predict(screen())
        self._handle_regimg(p)

    def play_round1(self) -> None:
        self.fill()
        paths = search(self.table, shuffle=True)

        # in this game if you mark all symbols in the first round,
        # then instantly after you mark the last symbol from table,
        # you automatically end the round, so better at beginning mark
        # all words which don't includes a cell, after mark all which
        # includes (in the first round is one word, after which round
        # will be end)

        last_cell = 0, 0  # cell which bot will visit the last

        last_cell_paths = []
        for p in paths:
            if last_cell in p:
                last_cell_paths.append(p)
            else:
                self._press_word(p)

        for p in last_cell_paths:
            self._press_word(p)

    def play_round2(self) -> None:
        for p in search(self.table, shuffle=True):
            self._press_word(p)

    def reset(self) -> None:
        """Mark some variables as non-actual"""
        print("reset")
        self._screen = None
        self._table = None
        self._table_box = None

    def fill(self) -> None:
        """Fill an empty table at the screen with letters"""
        for i in range(n):
            wrd = next(_wrds)
            for j, ch in enumerate(wrd):
                self._move_cursor_to_cell(i, j)
                clicklib.click()
                _press_rus_char(ch)

    def press_all_table_words(self) -> None:
        print("all words pressing")
        paths = search(self.table, shuffle=True)
        for p in paths:
            self._press_word(p)

    def _handle_regimg(self, ri: regimg.RegImg):
        ev: event = ri.name  # type: ignore

        if ev in [
            "disconnect",
            "home",
            "round1help1",
            "round1help2",
            "roundend",
            "start",
            "who",
            "winner",
            "wordchoose",
        ]:
            clicklib.click(ri.points[0])
        elif ev == "round1help1":
            clicklib.mouse_down()
            pg.move(-100)
            clicklib.mouse_up()
        elif ev == "playing":
            top_left = ri.points[0]
            bottom_right = ri.points[1]
            self.reset()
            self._table_box = (*top_left, *bottom_right)
            self.play_round1()

    @property
    def table(self) -> list[str]:
        """Return the content of a table at the screen."""
        if self._table is None:
            self._extract_table()
        return self._table  # type: ignore

    @property
    def table_box(self) -> Rect:
        """Return the box of a letter table at the screen."""
        assert self._table_box != None
        return self._table_box  # type: ignore

    @property
    def table_start(self) -> tuple[int, int]:
        """Return the position where a table at the screen is started."""
        x0, y0, _, _ = self.table_box
        return x0, y0

    def _extract_table(self) -> None:
        """Extract from the screen a letter table and return nothing.

        Save the result into the respective variables."""
        print("extract table")

        img = self.screen.crop(self.table_box)
        self._table = extract_table(img)

        for row in self._table:
            print(row)

    @property
    def screen(self) -> Image.Image:
        """Return the screenshot image of the screen."""
        if self._screen is None:
            self._make_screen()
        return self._screen  # type: ignore

    def _make_screen(self) -> None:
        """Do a screenshot, save the result into the respective variable."""
        print("make screen")
        self._screen = screen()

    @property
    def table_image_size(self) -> tuple[int, int]:
        x0, y0, x1, y1 = self.table_box
        return x1 - x0, y1 - y0

    def _move_cursor_to_cell(self, i: int, j: int) -> None:
        hsz, vsz = self._cell_sizes
        x0, y0 = self.table_start
        w, h = self.table_image_size
        if i == 0:
            y0 += (w / n) * 0.2
        if j == 0:
            x0 += (h / n) * 0.2
        # pg.moveTo(x0 + j * hsz, y0 + i * vsz, duration=DURATION)
        x0, y0 = int(x0), int(y0)
        clicklib.move(x0 + j * hsz, y0 + i * vsz, duration=DURATION)

    def _press_word(self, path: WordPath):
        """Press a word with the word path at the letter table at the screen."""
        print(f"press a word ({len(path)})")
        self._move_cursor_to_cell(*path[0])
        clicklib.click()
        clicklib.mouse_down()
        for i, j in path:
            self._move_cursor_to_cell(i, j)
        clicklib.mouse_up()

    @property
    def _cell_sizes(self) -> tuple[int, int]:
        """Get a tuple from table cell sizes.

        The first element is horizontal size, the second is vertical"""
        w, h = self.table_image_size
        k = 1.2  # is chosen randomly
        hsz = int(k * (w / n))
        vsz = int(k * (h / n))
        return hsz, vsz


if __name__ == "__main__":
    gamer = Gamer()
    while True:
        act = input(
            """ press anything:
 1 - auto-playing 1st round
 2 - auto-playing 2nd round
 q - exit this shell
 dict - sync the dict.txt file:dict.txt:
 :"""
        )
        if act == "dict":
            sync_words_with_dict()
        elif act == "q":
            break
        elif act == "1":
            gamer.play_round1()
        elif act == "2":
            gamer.play_round2()
        elif act == "show":
            box = extract_table_image(gamer.screen)
            img = gamer.screen.crop(box)
            photo.normalize_table_image(img).show()
        else:
            print("do nothing")
