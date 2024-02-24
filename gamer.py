import random
import time
from typing import Literal

import pyautogui as pg
from PIL import Image

import clicklib
import regimg
from photo import Rect
from screener import screen
from tsrct import extract_table, read_text_at_img_fragment
from worder import (
    WordPath,
    n,
    random_5letters_words,
    save_word_to_dict,
    search,
    sync_words_with_dict,
    trim_dict,
)

DURATION = 0.1
EVENTS_SLEEP_TIME = 2
RELOAD_PAGE_TIME = 60

WORDCHOOSE_LABEL_TEXT = "впиши слово"

# the amount of time in second what bot will wait after the first round is end
MAX_PLAYER_WAITING = 200

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
        self._rescroll()

    @staticmethod
    def _rescroll():
        # w = pg.size().width
        # h = pg.size().height
        # clicklib.move(h // 2, w)
        clicklib.click()
        clicklib.scroll(10)
        clicklib.scroll(-1)

    def restart(self):
        pg.hotkey("ctrl", "r")
        time.sleep(60)
        self._rescroll()

    def start(self):
        wait_player_time = 0
        prev = None

        while True:
            time.sleep(EVENTS_SLEEP_TIME)
            self._make_screen()
            assert self._screen is not None
            p = regimg.predict(self._screen)

            if prev == "playing" and p.name == "playing":
                # don't play twice at the same round
                continue

            wait_player_time += EVENTS_SLEEP_TIME
            wait_player_time *= p.name == "rounded"
            if wait_player_time > MAX_PLAYER_WAITING:
                self.restart()
                time.sleep(RELOAD_PAGE_TIME)

            self._handle_regimg(p, self._screen)
            prev = p.name

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

        # mark all rows just for fun
        for i in range(n):
            self._move_cursor_to_cell(i, 0)
            clicklib.click()
            clicklib.mouse_down()
            self._move_cursor_to_cell(i, n - 1)
            clicklib.mouse_up()

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

    def _handle_regimg(self, ri: regimg.RegImg, scr: Image.Image | None = None):
        ev: event = ri.name  # type: ignore

        if ev in [
            "disconnect",
            "home",
            "round1help2",
            "roundend",
            "start",
            "who",
            "winner",
        ]:
            clicklib.click(ri.points[0])

        elif ev == "round1help1":
            clicklib.mouse_down()
            pg.move(-200)
            clicklib.mouse_up()

        elif ev == "playing":
            top_left = ri.points[0]
            bottom_right = ri.points[1]
            self.reset()
            self._table_box = (*top_left, *bottom_right)
            self.play_round1()

        elif ev == "wordchoose":
            _, _, xy = ri.points
            clicklib.click(xy)
            if scr is not None:
                self.save_recommended_word_to_dict(ri, scr)

        if ev == "winner":
            sync_words_with_dict()
            trim_dict(sync_words=False)

    def save_recommended_word_to_dict(self, ri: regimg.RegImg, scr: Image.Image):
        top_left, bottom_right, _ = ri.points
        box = (*top_left, *bottom_right)
        word = read_text_at_img_fragment(scr, box).lower().strip()
        if word != WORDCHOOSE_LABEL_TEXT:
            # gamer will sync the dict after winner with 30% change, so
            # now sync=False
            save_word_to_dict(word, sync=False)

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
        # w, h = self.table_image_size
        clicklib.move(
            int(x0 + (j + 0.5) * hsz),
            int(y0 + (i + 0.5) * vsz),
            duration=DURATION,
        )

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
        # k = 1.2  # is chosen randomly
        k = 1
        hsz = int(k * (w / n))
        vsz = int(k * (h / n))
        return hsz, vsz


g = None
if __name__ == "__main__":
    time.sleep(1)
    g = Gamer()
    g.start()
