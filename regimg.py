import os

import numpy as np
from PIL import Image

import photo


def _into_one_size(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    aw, ah = a.shape
    bw, bh = b.shape

    minh = min(ah, bh)
    minw = min(aw, bw)

    return a[:minw, :minh], b[:minw, :minh]


def prepare_image(img: Image.Image) -> np.ndarray:
    box = photo.extract_canvas_image(img)
    img = img.crop(box)
    img = img.convert("L")

    return np.array(img)


class RegImg:
    _img: np.ndarray
    _name: str | None

    def __init__(self, img: Image.Image, name: str | None = None):
        self._img = prepare_image(img)
        self._name = name

    @staticmethod
    def from_filename(filename: str, name: str | None = None) -> "RegImg":
        if name is None:
            name = filename
        img = Image.open(filename)
        ri = RegImg(img, name=os.path.basename(filename))
        return ri

    def match_with_img(self, img: Image.Image) -> int:
        a = np.array(img.convert("L"))
        return self.match_value(a)

    def match_value(self, img: np.ndarray) -> int:
        # expected the numpy array representation of image with
        # mode="L"
        a, b = _into_one_size(self._img, img)
        w, h = a.shape
        res = (a == b).sum() / (w * h)
        return res


if __name__ == "__main__":
    cadrs_root = "./cadrs/"

    regimgs_root = "./regimgs/"
    rs = list(
        map(
            lambda f: RegImg.from_filename(regimgs_root + f, name=f.split(".")[0]),
            os.listdir(regimgs_root),
        )
    )

    for cadr_filename in os.listdir(cadrs_root):
        img = Image.open(cadrs_root + cadr_filename)
        a = prepare_image(img)

        print(
            cadr_filename,
            ":",
            max(
                rs,
                key=lambda ri: ri.match_value(a),
            )._name,
        )
