import easyocr
import numpy as np
from PIL import Image

from photo import Palette, Rect, add_padding, only_table_text, split_image_on_rows
from worder import N

WHITE_BG = 255

_reader = easyocr.Reader(["ru"])


def read_text_at_img_fragment(img: Image.Image, box: Rect):
    """Read the text from the part of a given img."""
    return _extract_text(img.crop(box))


def extract_table(img: Image.Image, palette: Palette, show=False) -> list[str]:
    """Extract the letters table of the game using a palette .

    Palette is list of Colors that you pick from DodoGame.
    """
    img = only_table_text(img, palette)

    if show:
        img.show()

    table = []

    for img_row in split_image_on_rows(img, N):
        row_txt = _extract_text(add_padding(img_row, 60, WHITE_BG))
        row_txt = _remove_whitespaces(row_txt).lower()
        row_txt = row_txt.ljust(N, ".")  # add dots . to make row with needed width
        table.append(row_txt)

    return table


def _remove_whitespaces(s: str):
    return s.replace(" ", "").replace("\n", "")


def _extract_text(img: Image.Image) -> str:
    img = np.array(img)  # type: ignore
    txt = "".join(_reader.readtext(img, detail=0))  # type: ignore
    txt = (
        txt.replace("0", "о")
        .replace("₽", "р")
        .replace("€", "с")
        .replace("%", "х")
        .replace("1", "пу")
        .replace("3", "з")
        .replace("4", "а")
        .replace("6", "б")
        .replace("7", "п")
    )
    return txt
