from screener import screen
from tsrct import extract_table
from worder import search


def print_words() -> None:
    tbl = extract_table(screen(), show=False)
    _print_table(tbl)
    search(tbl, show=True)


def _print_table(table: list[str]) -> None:
    for row in table:
        print(row)


if __name__ == "__main__":
    print_words()
