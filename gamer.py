import pyautogui as pg
from PIL import Image

from photo import Box, extract_table_image
from screener import screen
from tsrct import extract_table
from worder import WordPath, n, search


class Gamer:
    _table: list[str] | None
    _table_box: Box | None
    _screen: Image.Image | None

    def reset(self) -> None:
        """Mark some variables as non-actual"""
        print("reset")
        self._screen = None
        self._table = None
        self._table_box = None

    def press_all_table_words(self) -> None:
        print("all words pressing")
        paths = search(self.table)
        for p in paths:
            self._press_word(p)

    @property
    def table_box(self) -> Box:
        """Return the box of a letter table at the screen."""
        if self._table_box is None:
            self._extract_table()
        return self._table_box  # type: ignore

    @property
    def table(self) -> list[str]:
        """Return the content of a table at the screen."""
        if self._table is None:
            self._extract_table()
        return self._table  # type: ignore

    def _extract_table(self) -> None:
        """Extract from the screen a letter table and return nothing.

        Save the result into the respective variables."""
        print("extract table")
        self._table_box, img = extract_table_image(self.screen)
        self._table = extract_table(img)

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

    def _press_word(self, path: WordPath):
        """Press a word with the word path at the letter table at the screen."""
        print("press a word")
        duration = 0.2
        w, h = self.table_image_size
        x0, y0, _, _ = self.table_box
        hsz = int(1.2 * (w / n))
        vsz = int(1.2 * (h / n))
        i, j = path.first
        pg.moveTo(x0 + j * hsz, y0 + i * vsz, duration=duration)
        pg.click()
        pg.mouseDown()
        for i, j in path.rest:
            pg.moveTo(x0 + j * hsz, y0 + i * vsz, duration=duration)
        pg.mouseUp()


if __name__ == "__main__":
    gamer = Gamer()
    while True:
        _ = input('press Enter to new "auto-gaming"')
        gamer.reset()
        gamer.press_all_table_words()
