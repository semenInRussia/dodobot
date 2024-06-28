import time
import traceback
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Iterator, Union

import pyautogui as pg
from PIL import Image

import clicklib
import photo
import regimg
import vision
import worder
from photo import Rect
from screener import screen
from scroller import rescroll
from worder import WordPath, n, save_word_to_dict, search, trim_dict

SAME_SCENES_MAX_PROCESS_TIME = timedelta(minutes=4)
RELOAD_PAGE_INTERVAL = timedelta(minutes=40)
PLAYING_ROUND_TIME = timedelta(minutes=2, seconds=47)
FULL_ROUND_TIME = timedelta(minutes=3)

WORDCHOOSE_SCREENS_AMOUNT = 10

DURATION = 0.01
TIMEOUT_BETWEEN_SCENES = 2
RELOAD_PAGE_TIME = 60

WORDCHOOSE_LABEL_TEXT = "впиши слово"

# the amount of time in second what bot will wait after the first round is end
MAX_PLAYER_WAITING = 200

rus_keyboard = "йцукенгшщзхъфывапролджэячсмитьбю"
eng_keyboard = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
_rus_to_eng = dict(zip(rus_keyboard, eng_keyboard))


def _is_ok_start_word(w: str) -> bool:
    return len(w) == n and "ь" not in w and "ё" not in w


def start_words() -> Iterator[str]:
    sw = list(filter(_is_ok_start_word, worder.words))
    sw = [w for w in worder.words if _is_ok_start_word(w)]

    while True:
        yield from sw


def _press_rus_char(ch: str) -> None:
    pg.press(_rus_to_eng.get(ch, ""))


def _row_words_paths() -> Iterable[WordPath]:
    return map(_row_word_path, range(n - 1, -1, -1))


def _row_word_path(i: int) -> WordPath:
    """Return a word path from the left cell to right cell of i-th row."""
    return list(map(lambda j: (i, j), range(n)))  # noqa


class Gamer:
    _screen: Union[Image.Image, None] = None

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

    def reset(self) -> None:
        """Mark some variables as non-actual.

        MUST be called before every scene.
        """
        print("reset")
        self._screen = None
        self._table = None
        self._table_box = None

    def start(self):
        """Start work, endless gaming to the Dodo Game."""
        prev = None
        same_scenes_start_time = datetime.now()

        while True:
            time.sleep(TIMEOUT_BETWEEN_SCENES)
            self.reset()
            scene = self._predict_scene(self.screen)
            print(f"Give a new scene: {scene.name}")

            if prev == "playing" and scene.name == "playing":
                # don't play twice at the same round
                continue

            if (
                prev == scene.name
                and datetime.now() - same_scenes_start_time
                >= SAME_SCENES_MAX_PROCESS_TIME
            ):
                self.reload_page()
                same_scenes_start_time = datetime.now()

            if prev != scene.name:
                same_scenes_start_time = datetime.now()

            self._handle_scene(scene, self.screen)
            prev = scene.name

    def _predict_scene(self, img: Image.Image) -> regimg.RegImg:
        try:
            s = self._predicter.predict(img)
        except ValueError:
            return regimg.NullRegImg
        else:
            return s

    def _handle_scene(self, ri: regimg.RegImg, scr: Image.Image | None = None):
        sc = ri.name

        if sc in [
            "disconnect",
            "home",
            "round1help2",
            "roundend",
            "start",
            "who",
            "winner",
        ]:
            clicklib.click(*ri.points[0])

        elif sc == "round1help1":
            clicklib.mouse_down()
            pg.move(-200)
            clicklib.mouse_up()

        elif sc == "help":
            self.reload_page()

        elif sc == "playing":
            top_left = ri.points[0]
            bottom_right = ri.points[1]
            self.reset()
            self._table_box = (*top_left, *bottom_right)
            self.play_round()

        elif sc == "wordchoose":
            _, _, xy = ri.points
            for _ in range(WORDCHOOSE_SCREENS_AMOUNT):
                clicklib.click(*xy)
                if scr is not None:
                    self.save_recommended_word_to_dict(ri, screen())

        if sc == "winner":
            trim_dict()
            self._reload_page_if_time_is_come()

    def _reload_page_if_time_is_come(self) -> None:
        uptime = datetime.now() - self._last_reboot_time
        if uptime > RELOAD_PAGE_INTERVAL:
            self.reload_page()

    def reload_page(self):
        self.reset()
        rescroll()
        pg.hotkey("ctrl", "r")
        self._last_reboot_time = datetime.now()
        time.sleep(60)
        self._rescroll()

    @staticmethod
    def _rescroll():
        rescroll()

    def play_round(self) -> None:
        """Play the round, consider that this round is first.

        Even if this round is second it's still works.  This must be
        called only when the table of letters (maybe empty and without
        letters) is visible
        """
        round_start = datetime.now()

        # fill the table with letters
        #
        # table have rows, fill these rows with exiting words
        self.fill()

        # ignore all words which are rows in table, it useful for 1st
        # round, because in 100% cases mark all symbols in table, so
        # x2 is guaranteed.  The main is to mark them at the end
        paths = search(self.table, shuffle=True, ignored_words=self.table)

        # in this game if you select all symbols in the first round,
        # then instantly after you select the last symbol from the
        # table, the round will be automatically ended.  So better at
        # the beginning select all words which don't includes the same
        # cell, when bot selected them, it select also all row,
        # because they are also words (see below), after select all
        # words which include that symbol

        # sometimes needed to mark all row words.  I choose the row
        # words from the dict, so they must be exist words, above I
        # use the parameter worder.search.ignored_words it's
        # guaranteed that words aren't marked yet if mark all row
        # words, then round is ended with x2
        row_paths_used = False

        last_cell = 0, 0  # cell which bot will visit the last
        last_cell_paths = []

        for p in paths:
            # if playing time is almost over, mark all symbols to do
            # x2
            #
            # strategy to mark ALL symbols is that make rows words and
            # mark them at the end
            round_time = datetime.now() - round_start
            if not row_paths_used and round_time >= PLAYING_ROUND_TIME:
                row_paths_used = True
                self._press_row_paths()

            if round_time >= FULL_ROUND_TIME:
                return

            if last_cell in p:
                last_cell_paths.append(p)
            else:
                self._press_word_path(p)

        if not row_paths_used:
            self._press_row_paths()

        for p in last_cell_paths:
            round_time = datetime.now() - round_start
            if round_time > FULL_ROUND_TIME:
                return
            self._press_word_path(p)

    @property
    def _cell_sizes(self) -> tuple[int, int]:
        """Get a tuple from table cell sizes.

        The first element is horizontal size, the second is vertical
        """
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

    def _press_word_path(self, path: WordPath):
        """Press a word with the word path at the letter table at the screen."""
        print(f"press a word ({len(path)})")
        clicklib.click(*self._cell_position(*path[0]))
        clicklib.mouse_down()
        for i, j in path:
            self._move_cursor_to_cell(i, j)
            clicklib.mouse_up()

    def _press_row_paths(self) -> None:
        for p in _row_words_paths():
            self._press_word_path(p)

    def fill(self) -> None:
        """Fill an empty table at the screen with letters."""
        for i in range(n):
            wrd = next(self._wrds)
            for j, ch in enumerate(wrd):
                clicklib.click(*self._cell_position(i, j))
                _press_rus_char(ch)

    def save_recommended_word_to_dict(self, ri: regimg.RegImg, scr: Image.Image):
        """Save a word, that game recommended to you into the dict.txt.

        When you choose a word to game, the game recommend you to
        choose any word, save this word to dict.txt.
        """
        top_left, bottom_right, _ = ri.points
        box = (*top_left, *bottom_right)
        word = vision.read_text_at_img_fragment(scr, box).lower().strip()
        if word != WORDCHOOSE_LABEL_TEXT:
            save_word_to_dict(word, show=True)

    @property
    def table(self) -> list[str]:
        """Return the content of a table at the screen."""
        if self._table is None:
            self._extract_table()
        return self._table  # type: ignore

    @property
    def table_box(self) -> Rect:
        """Return the box of a letters table at the screen.

        Box is boundaries of the object (left top and right bottom
        coordinates).
        """
        assert (
            self._table_box is not None
        ), "_table_box (table's bounds) must saved right after _predict_scene"
        return self._table_box  # type: ignore

    @property
    def table_start(self) -> tuple[int, int]:
        """Return the position where a table at the screen is started."""
        x0, y0, _, _ = self.table_box
        return x0, y0

    def _extract_table(self) -> None:
        """Extract from the screen the letters table and return nothing.

        Save the result into the respective variables.
        """
        print("extract table")

        img = self.screen.crop(self.table_box)
        self._table = vision.extract_table(img, self._palette)

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


def main() -> None:
    time.sleep(1)
    g = Gamer()
    while True:
        try:
            g.start()
        except KeyboardInterrupt:
            break
        except pg.FailSafeException:
            _ = input("press Enter to continue")
        except:  # noqa
            print(traceback.format_exc())


if __name__ == "__main__":
    main()
