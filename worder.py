import itertools
import random
from collections.abc import Iterator
from dataclasses import dataclass

n = 5
MAX_WORD_LEN = 7
words = set()


def sync_words_with_dict(path="dict.txt"):
    global words
    with open(path, "r") as f:
        words = set(map(str.strip, f))


sync_words_with_dict()

Point = tuple[int, int]

"""
This is a list of deltas for the current point to the next possible point.

Every element is a tuple from two values:

- the first is a change of `i`: a table row
- the second is a change of `j`: a table column

Rows are numbered from the top to bottom.  Columns are numbered from
the left to right, so the delta (-1, -1) is the delta for up-left movement.

NOTE: that here straight movements are prefered over diag movements.
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


@dataclass
class WordPath:
    first: Point
    rest: list[Point]

    def __len__(self):
        return len(self.rest) + 1

    def add(self, d: Point):
        return WordPath(first=self.first, rest=self.rest + [d])


def _random_5letters_words() -> Iterator[str]:
    for wrd in words:
        if len(wrd) == 5:
            yield wrd


random_5letters_words = itertools.cycle(_random_5letters_words())


_checked_words: set[str] = set()
_used: list[list[bool]] = [[False for _ in range(n)] for _ in range(n)]
_table: list[str] = []
_paths: list[WordPath] = []


def search(table: list[str], show=False, shuffle=False) -> list[WordPath]:
    global _checked_words, _used, _table, _paths

    _checked_words = set()
    _paths = []
    _table = table

    for i in range(n):
        for j in range(n):
            path = WordPath(first=(i, j), rest=[])
            _fill_matrix(_used, False)
            _dfs(i, j, path=path, word="")

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


def _dfs(i: int, j: int, path: WordPath, word: str):
    global _checked_words, _used, _table, _paths

    if i < 0 or i >= n or j < 0 or j >= n:
        return
    if _used[i][j]:
        return

    word += _table[i][j]

    if word in words and len(word) > 1 and word not in _checked_words:
        _paths.append(path)
        _checked_words.add(word)

    if len(word) == MAX_WORD_LEN:
        return

    _used[i][j] = True

    for di, dj in _deltas:
        _dfs(i + di, j + dj, path=path.add((i + di, j + dj)), word=word)

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
    path = WordPath(first=(0, 1), rest=[])
    paths = search(tbl, show=True)
    for p in paths:
        print(p)
