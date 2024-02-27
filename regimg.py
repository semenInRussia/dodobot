import os
from typing import Callable, Iterator, Optional

import numpy as np
import pyautogui as pg
from PIL import Image

import photo


def _into_one_size(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    aw, ah = a.shape
    bw, bh = b.shape

    minh = min(ah, bh)
    minw = min(aw, bw)

    return a[:minw, :minh], b[:minw, :minh]


class RegImg:
    _img: np.ndarray
    name: Optional[str]
    points: list[tuple[int, int]]

    def __init__(self, img: Image.Image, name: Optional[str] = None):
        img = img.convert("RGBA")
        self._img = prepare_image(img)
        self.name = name
        self._save_targets(img)

    def click_to_target(self):
        if self.points:
            pg.moveTo(self.points[0])

    @staticmethod
    def from_filename(filename: str, name: Optional[str] = None) -> "RegImg":
        if name is None:
            # the name is the first of filename
            # parts separated with dots
            #
            # start.1.2.png => start
            # meow.15.png   => meow
            name = os.path.basename(filename).split(".")[0]
        img = Image.open(filename)
        ri = RegImg(img, name=name)
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

    def _save_targets(self, img: Image.Image) -> None:
        a = np.array(img)
        ys, xs = np.nonzero(a[:, :, 3] == 0)
        self.points = list(zip(xs, ys))


class Predicter:
    _ris: list[RegImg]
    _prepare_function: Optional[Callable]

    def __init__(self, regimgs: Iterator[RegImg], prepare_function=None):
        self._prepare_function = prepare_function
        self._ris = list(regimgs)

    @classmethod
    def from_directory(cls, root: str):
        if not root.endswith("/"):
            root += "/"
        files = os.listdir(root)
        files = filter(lambda f: f.endswith(".png"), files)
        files = map(lambda f: root + f, files)
        regimgs = map(RegImg.from_filename, files)
        return cls(regimgs)

    def predict(self, img: Image.Image) -> RegImg:
        if self._prepare_function:
            a = self._prepare_function(img)
        else:
            a = np.array(img.convert("L"))

        return max(self._ris, key=lambda r: r.match_value(a))


def prepare_image(img: Image.Image) -> np.ndarray:
    box = photo.extract_canvas_image(img)
    img = img.crop(box)
    img = img.convert("L")

    return np.array(img)


class GamePredicter(Predicter):
    def __init__(self, regimgs: Iterator[RegImg]):
        super().__init__(regimgs, prepare_function=prepare_image)


if __name__ == "__main__":
    gp = GamePredicter.from_directory("regimgs")

    for cadr_filename in os.listdir(cadrs_root):
        img = Image.open(cadrs_root + cadr_filename)
        print(cadr_filename, gp.predict(img).name)
