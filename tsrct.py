import numpy as np
import pytesseract
from PIL import Image

filename = "./screen.png"
Color = tuple[int, int, int, int]


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def extract_table(img: Image.Image, show=False) -> list[str]:
    img = _cvt_img(img)

    if show:
        img.show()

    text = pytesseract.image_to_string(img, lang="rus")
    print(text)
    text = text.replace(" ", "").replace("\n", "").lower()

    return list(_chunks(text, 5))


TEXT_COLOR = (26, 35, 37, 255)  # rgba
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def _cvt_img(img: Image.Image):
    img = _crop_2color_img(img, TEXT_COLOR)
    img = _only_text(img, TEXT_COLOR, BLACK, WHITE)

    return img


def _only_text(img: Image.Image, txt: Color, fg: Color, bg: Color) -> Image.Image:
    a = np.array(img)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    msk = (r == txt[0]) & (g == txt[1]) & (b == txt[2])

    a[:, :, :][msk] = fg
    a[:, :, :][~msk] = bg

    return Image.fromarray(a)


def _crop_2color_img(img: Image.Image, fg: Color) -> Image.Image:
    w, h = img.size
    a = img.load()  # array

    # maximum possible
    beg_col = w
    beg_row = h

    # the same for col and row where it ended, defaults to min
    # possible
    end_col = 0
    end_row = 0

    for y in range(h):
        for x in range(w):
            if a[x, y] == fg:
                beg_col = min(beg_col, x)
                beg_row = min(beg_row, y)
                end_col = max(end_col, x)
                end_row = max(end_row, y)

    # beg col is where the first table pixel, make it on 3 pixels lefter
    # the same for other bounds
    pad = 0  # padding of text in image
    beg_col = max(0, beg_col - pad)
    beg_row = max(0, beg_row - pad)
    end_col = min(w - 1, end_col + pad)
    end_row = min(h - 1, end_row + pad)

    return img.crop((beg_col, beg_row, end_col, end_row))


if __name__ == "__main__":
    print(extract_table(Image.open(filename), show=True))
    # print(extract_table(Image.open("./testdata/s1.png"), show=True))
