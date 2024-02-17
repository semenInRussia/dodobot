_show = True
if _show:
    print("importing...")

from screener import screen
from tsrct import extract_table
from worder import search


def print_words(show=False) -> None:
    _maybe_print("screening...", show)
    img = screen()

    _maybe_print("extract text...", show)
    tbl = extract_table(img, show=False)
    _print_table(tbl)

    _maybe_print("searching...", show)
    search(tbl, show=show)


def _maybe_print(s: str, show=False, *args, **kwargs):
    if show:
        print(s, *args, **kwargs)


def _print_table(table: list[str]) -> None:
    for row in table:
        print(row)


if __name__ == "__main__":
    print_words(show=_show)
