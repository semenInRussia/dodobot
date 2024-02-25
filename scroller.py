import clicklib

SCROLL_POSITION = (1400, 600)


def rescroll() -> None:
    clicklib.click(SCROLL_POSITION)
    clicklib.scroll(10)
    clicklib.scroll(-1)


if __name__ == "__main__":
    while True:
        act = input("Enter Enter to rescroll, q to exit\n")
        if act == "q":
            break
        rescroll()
