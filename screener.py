from mss import mss
from PIL import Image


def screen() -> Image.Image:
    with mss() as s:
        s.shot()
        return Image.open("monitor-1.png")


if __name__ == "__main__":
    screen().show()
