import easyocr
import numpy as np
from PIL import Image

from photo import (
    WHITE,
    Rect,
    add_padding,
    extract_table_image,
    only_table_text,
    split_image_on_rows,
)
from worder import n

filename = "monitor-1.png"

_reader = easyocr.Reader(["ru"])


def read_text_at_img_fragment(img: Image.Image, box: Rect):
    return _extract_text(img.crop(box))


def extract_table(img: Image.Image, show=False) -> list[str]:
    img = only_table_text(img)

    if show:
        img.show()

    table = []
    WHITE_BG = 255

    for img_row in split_image_on_rows(img, n):
        img_row = add_padding(img_row, 60, WHITE_BG)
        row_txt = _extract_text(img_row)
        row_txt = row_txt.replace(" ", "").replace("\n", "").lower()
        table.append(row_txt.ljust(n, "."))

    return table


def _extract_text(img: Image.Image) -> str:
    img = np.array(img)  # type: ignore
    txt = _reader.readtext(img, detail=0)
    txt = "".join(txt)
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


if __name__ == "__main__":
    print(extract_table(Image.open(filename), show=True))
