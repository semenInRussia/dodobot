import easyocr
import numpy as np
from PIL import Image

from photo import cvt_img

filename = "./screen.png"

_reader = easyocr.Reader(["ru"])


def extract_table(img: Image.Image, show=False) -> list[str]:
    img = cvt_img(img)

    if show:
        img.show()

    text = _extract_text(img)
    text = text.replace(" ", "").replace("\n", "").lower()

    return list(_chunks(text, 5))


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _extract_text(img: Image.Image) -> str:
    img = np.array(img)  # type: ignore
    txt = _reader.readtext(img, detail=0)
    txt = "".join(txt)
    txt = (
        txt.replace("0", "о")
        .replace("₽", "р")
        .replace("€", "с")
        .replace("6", "б")
        .replace("3", "з")
    )
    return txt


if __name__ == "__main__":
    print(extract_table(Image.open(filename), show=True))
    # print(extract_table(Image.open("./testdata/s1.png"), show=True))
