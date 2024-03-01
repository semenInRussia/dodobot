import random
from collections.abc import Iterable
from typing import Optional

n = 5
MAX_WORD_LEN = 7
words: set[str] = set()


def sync_words_with_dict(path="dict.txt") -> None:
    global words
    with open(path) as f:
        words = set(map(str.strip, f))


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

_checked_words: set[str] = set()
_used: list[list[bool]] = [[False for _ in range(n)] for _ in range(n)]
_table: list[str] = []
_paths: list[WordPath] = []


def search(
    table: list[str],
    show=False,
    shuffle=False,
    ignored_words: Optional[Iterable[str]] = None,
) -> list[WordPath]:
    global _checked_words, _used, _table, _paths

    _checked_words = set()

    if ignored_words:
        _checked_words.update(ignored_words)

    _paths = []
    _table = table

    for i in range(n):
        for j in range(n):
            path = [(i, j)]
            _fill_matrix(_used, False)
            _dfs(i, j, path=path, word="")

    # at start the function I added these words as checked, because
    # need to ignore them, but now they marked as checked that is a
    # confusion
    if ignored_words:
        for w in ignored_words:
            _checked_words.discard(w)

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
    if (
        len(wrd) >= 3  # noqa
        and wrd[-1] in "еуюиы"
        and wrd[-2] not in "яуйцеъыаоэяию"
        and wrd[:-1] in words
    ):
        return True
    return wrd in words


def _dfs(i: int, j: int, path: WordPath, word: str):
    global _checked_words, _used, _table, _paths

    if i < 0 or i >= n or j < 0 or j >= n:
        return
    if _used[i][j]:
        return

    word += _table[i][j]

    if _is_word_exists(word) and word not in _checked_words:
        _paths.append(path)
        _checked_words.add(word)

    if len(word) == MAX_WORD_LEN:
        return

    _used[i][j] = True

    for di, dj in _deltas:
        _dfs(i + di, j + dj, path=path + [(i + di, j + dj)], word=word)

    _used[i][j] = False


# inplace
def _fill_matrix(m: list[list], val):
    if not m:
        return

    for i in range(len(m)):
        for j in range(len(m[0])):
            m[i][j] = val


if __name__ == "__main__":
    tbl = [
        "бвгде",
        "ёзилм",
        "журка",
        "нопст",
        "фхцшщ",
    ]
    path = [(0, 1)]
    paths = search(tbl, show=True, ignored_words=["лизун"])
    for p in paths:
        print(p)
