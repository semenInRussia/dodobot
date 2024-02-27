import os
from typing import Iterator, Union

import numpy as np
from PIL import Image

Color = Union[tuple[int, int, int, int], tuple[int, int, int]]

TEXT_COLOR = (26, 35, 37, 255)  # rgba
TABLE_BG = (250, 172, 113, 255)

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

N = 5


Rect = tuple[int, int, int, int]


def extract_canvas_image(img: Image.Image) -> Rect:
    cols = [(17, 27, 29), (238, 214, 177), (238, 214, 177), (34, 44, 46)]
    return _crop_region_with_colors(img, cols)


def extract_table_image(img: Image.Image) -> Rect:
    return _crop_region_with_colors(img, [TEXT_COLOR, TABLE_BG])


def only_table_text(img: Image.Image) -> Image.Image:
    return _only_text(img, TEXT_COLOR, BLACK, WHITE).convert(mode="L")


def split_image_on_rows(img: Image.Image, n: int) -> Iterator[Image.Image]:
    w, h = img.size
    sz = h // n
    for i in range(n):
        # x0, y0, x, y
        yield img.crop((0, sz * i, w, sz * i + sz))


def is_color_exists(img: Image.Image, col) -> bool:
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    m = (r == col[0]) & (g == col[1]) & (b == col[2])
    return m.any()


def _only_text(img: Image.Image, txt: Color, fg: Color, bg: Color) -> Image.Image:
    img = img.convert(mode="RGB")
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    msk = (r == txt[0]) & (g == txt[1]) & (b == txt[2])

    a[:, :, :][msk] = fg[:3]
    a[:, :, :][~msk] = bg[:3]

    return Image.fromarray(a)


def add_padding(img: Image.Image, pad: int, bg) -> Image.Image:
    w, h = img.size
    nsize = w + pad * 2, h + pad * 2
    padded = Image.new(img.mode, size=nsize, color=bg)
    padded.paste(img, (pad, pad))

    return padded


def _crop_region_with_colors(img: Image.Image, colors: list[Color]) -> Rect:
    """Find the biggest image region which contains all pixels with
    the given colors.

    Return the tuple (left, upper, right, down) of this image"""

    img = img.convert(mode="RGBA")
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

    msk = np.zeros_like(r)
    for col in colors:
        msk |= (r == col[0]) & (g == col[1]) & (b == col[2])

    x0 = np.min(_remove_zeros(msk.argmax(axis=1)))
    y0 = np.min(_remove_zeros(msk.argmax(axis=0)))
    x1 = max(map(_argmax_nonzero, msk))
    y1 = max(map(_argmax_nonzero, msk.T))

    return x0, y0, x1, y1


def _argmax_nonzero(arr: np.ndarray, default: int = -1) -> int:
    if arr.any():
        return int(np.max(arr.nonzero()))
    return default


def _remove_zeros(arr: np.ndarray) -> np.ndarray:
    return arr[arr != 0]


if __name__ == "__main__":
    root = "regimgs/"
    for filename in os.listdir(root):
        if not filename.endswith(".png"):
            continue
        img = Image.open(root + filename)
        box = extract_canvas_image(img)
        img.crop(box).show()
