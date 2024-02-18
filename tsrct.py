import easyocr
import numpy as np
from PIL import Image

from photo import normalize_table_image
from worder import n

filename = "./screen.png"

_reader = easyocr.Reader(["ru"])


def extract_table(img: Image.Image, show=False) -> list[str]:
    img = normalize_table_image(img)

    if show:
        img.show()

    txt = _extract_text(img)
    txt = txt.replace(" ", "").replace("\n", "").lower()
    txt += (n * n - len(txt)) * "."

    return list(_chunks(txt, 5))


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
        .replace("7", "п")
        .replace("4", "а")
        .replace("6", "б")
        .replace("3", "з")
    )
    return txt


if __name__ == "__main__":
    print(extract_table(Image.open(filename), show=True))
    # print(extract_table(Image.open("./testdata/s1.png"), show=True))
