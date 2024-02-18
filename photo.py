from collections.abc import Iterator

import numpy as np
from cv2 import norm
from PIL import Image

Color = tuple[int, int, int, int]

TEXT_COLOR = (26, 35, 37, 255)  # rgba
TABLE_BG = (250, 172, 113, 255)

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

N = 5


Box = tuple[int, int, int, int]


def extract_table_image(img: Image.Image) -> tuple[Box, Image.Image]:
    return _crop_region_with_color(img, TEXT_COLOR)


def normalize_table_image(img: Image.Image):
    img = _only_text(img, TEXT_COLOR, BLACK, WHITE)
    img = _add_padding(img, 30, WHITE)

    return img.convert(mode="L")


def _only_text(img: Image.Image, txt: Color, fg: Color, bg: Color) -> Image.Image:
    img = img.convert(mode="RGB")
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    msk = (r == txt[0]) & (g == txt[1]) & (b == txt[2])

    a[:, :, :][msk] = fg[:3]
    a[:, :, :][~msk] = bg[:3]

    return Image.fromarray(a)


def _add_padding(img: Image.Image, pad: int, bg: Color) -> Image.Image:
    w, h = img.size
    nsize = w + pad * 2, h + pad * 2
    padded = Image.new(img.mode, size=nsize, color=bg)
    padded.paste(img, (pad, pad))

    return padded


def _crop_region_with_color(img: Image.Image, color: Color) -> tuple[Box, Image.Image]:
    img = img.convert(mode="RGB")
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    msk = (r == color[0]) & (g == color[1]) & (b == color[2])

    x0 = np.min(_remove_zeros(msk.argmax(axis=1)))
    y0 = np.min(_remove_zeros(msk.argmax(axis=0)))
    x1 = max(map(_argmax_nonzero, msk))
    y1 = max(map(_argmax_nonzero, msk.T))

    box = x0, y0, x1, y1

    return box, img.crop(box)


def _argmax_nonzero(arr: np.ndarray, default: int = -1) -> int:
    if arr.any():
        return int(np.max(arr.nonzero()))
    return default


def _remove_zeros(arr: np.ndarray) -> np.ndarray:
    return arr[arr != 0]


# 62*5*x + 10*4*x = w
# 310x + 40x = w
# x = 350

if __name__ == "__main__":
    img = Image.open("monitor-1.png")
    _, img = extract_table_image(img)
    img = normalize_table_image(img)

    img.show()
