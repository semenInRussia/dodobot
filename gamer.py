import time
import traceback
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Iterator

import pyautogui as pg
from PIL import Image

import clicklib
import photo
import regimg
import worder
from photo import Rect
from screener import screen
from scroller import rescroll
from tsrct import extract_table, read_text_at_img_fragment
from worder import WordPath, n, save_word_to_dict, search, trim_dict

ONE_EVENT_HANDLE_MAX_TIME = timedelta(minutes=5)
RESTART_INTERVAL = timedelta(minutes=40)
PLAYING_ROUND_TIME = timedelta(minutes=2, seconds=47)

WORDCHOOSE_SCREENS_AMOUNT = 10

DURATION = 0.01
EVENTS_SLEEP_TIME = 2
RELOAD_PAGE_TIME = 60

WORDCHOOSE_LABEL_TEXT = "впиши слово"

# the amount of time in second what bot will wait after the first round is end
MAX_PLAYER_WAITING = 200

rus_keyboard = "йцукенгшщзхъфывапролджэячсмитьбю"
eng_keyboard = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
_rus_to_eng = dict(zip(rus_keyboard, eng_keyboard))


def _is_ok_start_word(w: str) -> bool:
    return len(w) == 5 and "ь" not in w and "ё" not in w


def start_words():
    sw = []

    for w in worder.words:
        if _is_ok_start_word(w):
            sw.append(w)

    while True:
        yield from sw


def _press_rus_char(ch: str) -> None:
    pg.press(_rus_to_eng.get(ch, ""))


def _row_words_paths() -> Iterable[WordPath]:
    return map(_row_word_path, range(n - 1, -1, -1))


def _row_word_path(i: int) -> WordPath:
    """Return a word path from the left cell to right cell of i-th row."""
    return list(map(lambda j: (i, j), range(n)))


class Gamer:
    _screen: Image.Image | None = None

    # for round playing
    _table: list[str] | None = None
    _table_box: Rect | None = None
    _wrds: Iterator[str]

    # for .start
    _last_reboot_time: datetime

    def __init__(self, words=None, predicter=None, palette=None):
        self.reset()
        self._rescroll()
        self._last_reboot_time = datetime.now()
        self._wrds = words or start_words()
        self._predicter = predicter or regimg.GamePredicter.from_directory("regimgs")
        self._palette = palette or photo.read_palette("regimgs/palette")

    @staticmethod
    def _rescroll():
        rescroll()

    def _restart_if_time_is_come(self) -> None:
        uptime = datetime.now() - self._last_reboot_time
        if uptime > RESTART_INTERVAL:
            self.restart()

    def restart(self):
        self.reset()
        rescroll()
        pg.hotkey("ctrl", "r")
        self._last_reboot_time = datetime.now()
        time.sleep(60)
        self._rescroll()

    def start(self):
        prev = None
        event_handle_time = 0

        while True:
            time.sleep(EVENTS_SLEEP_TIME)
            self.reset()
            p = self._predict_image(self.screen)
            print(f"event: {p.name}")

            if prev == "playing" and p.name == "playing":
                # don't play twice at the same round
                continue

            if prev == p.name:
                if timedelta(seconds=event_handle_time) > ONE_EVENT_HANDLE_MAX_TIME:
                    self.restart()
                    event_handle_time = 0
                event_handle_time += EVENTS_SLEEP_TIME
            else:
                event_handle_time = 0

            self._handle_regimg(p, self.screen)
            prev = p.name

    def _predict_image(self, img: Image.Image) -> regimg.RegImg:
        try:
            p = self._predicter.predict(img)
        except ValueError:
            return regimg.NullRegImg
        else:
            return p

    def play_round(self) -> None:
        round_start = datetime.now()

        # fill the table with letters
        self.fill()

        # ignore all words which are rows in table, it useful for 1st
        # round, because in 100% cases mark all symbols in table, so
        # x2 is guaranteed.  The main is to mark them at the end
        paths = search(self.table, shuffle=True, ignored_words=self.table)

        # in this game if you mark all symbols in the first round,
        # then instantly after you mark the last symbol from table,
        # you automatically end the round, so better at beginning mark
        # all words which don't includes a cell, after mark all which
        # includes (in the first round is one word, after which round
        # will be end)

        # sometimes needed to mark all row words.  I choose the row
        # words from the dict, so they must be exist words, above I
        # use the parameter worder.search.ignored_words it's
        # guaranteed that words aren't marked yet if mark all row
        # words, then round is ended with x2
        row_paths_used = False

        last_cell = 0, 0  # cell which bot will visit the last
        last_cell_paths = []

        for p in paths:
            # if playing time is up, mark all symbols to do x2
            round_time = datetime.now() - round_start
            if not row_paths_used and round_time >= PLAYING_ROUND_TIME:
                row_paths_used = True
                self._press_row_words()

            if last_cell in p:
                last_cell_paths.append(p)
            else:
                self._press_word(p)

        if not row_paths_used:
            self._press_row_words()

        for p in last_cell_paths:
            self._press_word(p)

    def _press_row_words(self) -> None:
        for p in _row_words_paths():
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
            wrd = next(self._wrds)
            for j, ch in enumerate(wrd):
                clicklib.click(self._cell_position(i, j))
                _press_rus_char(ch)

    def _handle_regimg(self, ri: regimg.RegImg, scr: Image.Image | None = None):
        ev = ri.name  # type: ignore

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

        elif ev == "help":
            self.restart()

        elif ev == "playing":
            top_left = ri.points[0]
            bottom_right = ri.points[1]
            self.reset()
            self._table_box = (*top_left, *bottom_right)
            self.play_round()

        elif ev == "wordchoose":
            _, _, xy = ri.points
            for _ in range(WORDCHOOSE_SCREENS_AMOUNT):
                clicklib.click(xy)
                if scr is not None:
                    self.save_recommended_word_to_dict(ri, screen())

        if ev == "winner":
            trim_dict()
            self._restart_if_time_is_come()

    def save_recommended_word_to_dict(self, ri: regimg.RegImg, scr: Image.Image):
        top_left, bottom_right, _ = ri.points
        box = (*top_left, *bottom_right)
        word = read_text_at_img_fragment(scr, box).lower().strip()
        if word != WORDCHOOSE_LABEL_TEXT:
            # gamer will sync the dict after winner with 30% change, so
            # now sync=False
            save_word_to_dict(word, show=True)

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
        self._table = extract_table(img, self._palette)

        for row in self._table:
            print(row)

    @property
    def screen(self) -> Image.Image:
        """Return the screenshot image of the screen."""
        if self._screen is None:
            self._make_screen()
        assert self._screen is not None
        return self._screen

    def _make_screen(self) -> None:
        """Do a screenshot, save the result into the respective variable."""
        print("make screen")
        self._screen = screen()

    @property
    def table_image_size(self) -> tuple[int, int]:
        x0, y0, x1, y1 = self.table_box
        return x1 - x0, y1 - y0

    @property
    def _cell_sizes(self) -> tuple[int, int]:
        """Get a tuple from table cell sizes.

        The first element is horizontal size, the second is vertical"""
        w, h = self.table_image_size
        return w // n, h // n

    def _move_cursor_to_cell(self, i: int, j: int) -> None:
        clicklib.move(*self._cell_position(i, j), duration=DURATION)

    def _cell_position(self, i: int, j: int) -> tuple[int, int]:
        hsz, vsz = self._cell_sizes
        x0, y0 = self.table_start
        return (
            int(x0 + (j + 0.5) * hsz),  # x
            int(y0 + (i + 0.5) * vsz),  # y
        )

    def _press_word(self, path: WordPath):
        """Press a word with the word path at the letter table at the screen."""
        print(f"press a word ({len(path)})")
        clicklib.click(self._cell_position(*path[0]))
        clicklib.mouse_down()
        for i, j in path:
            self._move_cursor_to_cell(i, j)
        clicklib.mouse_up()


g = None
if __name__ == "__main__":
    time.sleep(1)
    g = Gamer()
    while True:
        try:
            g.start()
        except KeyboardInterrupt:
            break
        except pg.FailSafeException:
            _ = input("press Enter to continue")
        except:
            print(traceback.format_exc())
