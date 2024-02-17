from pprint import pprint

from screener import screen
from tsrct import extract_table
from worder import search


def print_words():
    img = screen()
    tbl = extract_table(img, show=True)
    pprint(tbl)
    search(tbl, show=True)


print_words()
