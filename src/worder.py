import random
from collections.abc import Iterable
import time
from typing import Optional

from trie import Trie

N = 5
MAX_WORD_LEN = 20
words: Trie = Trie()


def sync_words_with_dict(path="dict.txt") -> None:
    global words
    with open(path) as f:
        words = Trie(map(str.strip, f))


def trim_dict(path="dict.txt", sync_words=True) -> None:
    if sync_words:
        sync_words_with_dict(path)
    s = ""
    for w in words:
        s += w + "\n"
    with open(path, "w") as f:
        f.write(s)


sync_words_with_dict()


def save_word_to_dict(word: str, path: str = "dict.txt", show: bool = False) -> None:
    global words

    if word not in words:
        words.add(word)
        with open(path, "a") as f:
            f.write(word + "\n")

    if show:
        print(f"amount of words is {len(words)}")


Point = tuple[int, int]

"""
This is a list of deltas for the current point to the next possible point.

Every element is a tuple from two values:

- the first is a change of `i`: a table row
- the second is a change of `j`: a table column

Rows are numbered from the top to bottom.  Columns are numbered from
the left to right, so the delta (-1, -1) is the delta for up-left movement.

NOTE: that here straight movements are preferred over diag movements.
"""
_deltas: list[Point] = [
    # straight movements
    (0, -1),  # left
    (0, +1),  # right
    (-1, 0),  # up
    (+1, 0),  # down
    # diag movements
    (+1, -1),  # down-left
    (-1, -1),  # up-left
    (-1, +1),  # up-right
    (+1, +1),  # down-right
]

WordPath = list[Point]

_checked_words: Trie = Trie()
_used: list[list[bool]] = [[False for _ in range(N)] for _ in range(N)]
_table: list[str] = []
_paths: list[WordPath] = []


def search(
    table: list[str],
    show=False,
    shuffle=False,
    ignored_words: Optional[Iterable[str]] = None,
) -> list[WordPath]:
    """Search in the table of letters all existing words.

    Word can be selected starting from any letter and continue to
    next letter with each of possible sides (including diagonals).

    For example in this table:

    cat
    ddr

    You can chose words cat or car (maybe also other words are exist)

    Return the list of paths where each of them is list of coordinates in
    the table, every path is represents any word.

    If ignored_words is True, don't return their paths if they are
    exists in the table

    If show is True, debug the words we search

    If shuffle is True, shuffle the order of resulting paths.  The
    default order is order how words are go when use `dfs`.
    """
    global _checked_words, _used, _table, _paths

    _checked_words.clear()

    if ignored_words:
        _checked_words.update(ignored_words)

    _paths = []
    _table = table

    for i in range(N):
        for j in range(N):
            path = [(i, j)]
            _dfs(i, j, path=path, word="")

    # at the beginning of the function I added these words as checked,
    # because need to ignore them, but now they marked as checked that
    # is a confusion
    if ignored_words:
        _checked_words.discard(ignored_words)

    if shuffle:
        random.shuffle(_paths)

    if show:
        _show_checked_words()

    return _paths


def _show_checked_words():
    for w in _checked_words:
        print(w)
    nwords = len(_checked_words)
    print(f"I found {nwords} words")


def _is_word_exists(wrd: str) -> bool:
    # 1. check the forms of wrd, remove the ending and check the word
    # before it, if exists that word is also exist
    if (
        len(wrd) >= 3  # noqa
        and wrd[-1] in "еуюиы"  # the last letter is ok ending
        and wrd[-2] not in "яуйцеъыаоэяию"  # the pre-last letter is ok with ending
        # the word without ending is ok
        and (wrd[:-1] in words or any((wrd[:-1] + end in words) for end in "яаь"))
    ):
        return True
    return len(wrd) > 1 and wrd in words


def _dfs(i: int, j: int, path: WordPath, word: str):
    global _checked_words, _used, _table, _paths

    if i < 0 or i >= N or j < 0 or j >= N:
        return
    if _used[i][j]:
        return

    word += _table[i][j]

    if _is_word_exists(word) and word not in _checked_words:
        _paths.append(path)
        _checked_words.add(word)

    if len(word) == MAX_WORD_LEN or not words.have_prefix(word):
        return

    _used[i][j] = True

    for di, dj in _deltas:
        _dfs(i + di, j + dj, path=path + [(i + di, j + dj)], word=word)

    _used[i][j] = False


if __name__ == "__main__":
    tbl = [
        "сково",
        "морор",
        "надео",
        "точкд",
        "надае",
    ]
    start = time.time()
    print(len(words.arr))
    paths = search(tbl, show=True, ignored_words=["лизун"])
    print((time.time() - start) * 1000)
    print(f"cnt = {len(_checked_words)}")
