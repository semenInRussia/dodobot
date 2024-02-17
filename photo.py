from collections.abc import Iterator

import numpy as np
from PIL import Image, ImageOps

Color = tuple[int, int, int, int]

TEXT_COLOR = (26, 35, 37, 255)  # rgba
TABLE_BG = (250, 172, 113, 255)

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

N = 5


def cvt_img(img: Image.Image):
    img = img.convert(mode="RGBA")
    img = _crop_region_with_color(img, [TEXT_COLOR])
    img = _only_text(img, TEXT_COLOR, BLACK, WHITE)
    img = _add_padding(img, 30, WHITE)

    return img.convert(mode="L")


def _only_text(img: Image.Image, txt: Color, fg: Color, bg: Color) -> Image.Image:
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    msk = (r == txt[0]) & (g == txt[1]) & (b == txt[2])

    a[:, :, :][msk] = fg
    a[:, :, :][~msk] = bg

    return Image.fromarray(a)


def _add_padding(img: Image.Image, pad: int, bg: Color) -> Image.Image:
    w, h = img.size
    nsize = w + pad * 2, h + pad * 2
    padded = Image.new(img.mode, size=nsize, color=bg)
    padded.paste(img, (pad, pad))

    return padded


def _crop_region_with_color(img: Image.Image, colors: list[Color]) -> Image.Image:
    w, h = img.size
    x0, y0, x1, y1 = w, h, 0, 0
    for x in range(w):
        for y in range(h):
            if img.getpixel((x, y)) in colors:
                x0 = min(x, x0)
                y0 = min(y, y0)
                x1 = max(x, x1)
                y1 = max(y, y1)

    return img.crop((x0, y0, x1, y1))


# 62*5*x + 10*4*x = w
# 310x + 40x = w
# x = 350

if __name__ == "__main__":
    img = Image.open("monitor-1.png")
    img = cvt_img(img)

    img.show()
