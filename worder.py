from dataclasses import dataclass
from enum import Enum

n = 5
MAX_WORD_LEN = 6

words = set()

with open("dict.txt", "r") as f:
    words = set(map(str.strip, f))


class Dir(Enum):
    upl = 1
    up = 2
    upr = 3
    r = 4
    downr = 5
    down = 6
    downl = 7
    l = 8


dirs = [
    (Dir.upl, (-1, -1)),
    (Dir.up, (-1, 0)),
    (Dir.upr, (-1, +1)),
    (Dir.r, (0, +1)),
    (Dir.downr, (+1, +1)),
    (Dir.down, (+1, 0)),
    (Dir.downl, (+1, -1)),
    (Dir.l, (0, -1)),
]


@dataclass
class Path:
    first: tuple[int, int]
    rest: list[Dir]

    def add(self, d: Dir):
        return Path(first=self.first, rest=self.rest + [d])


_checked_words: set[str] = set()
_used: list[list[bool]] = []
_table: list[str] = []
_paths: list[Path] = []


def search(table: list[str]) -> list[Path]:
    global _checked_words, _used, _table, _paths

    _checked_words = set()
    _paths = []
    _table = table

    for i in range(n):
        for j in range(n):
            _used = [[False] * n] * n
            _dfs(
                i,
                j,
                path=Path(first=(i, j), rest=[]),
                word="",
            )

    return _paths


def _dfs(
    i: int,
    j: int,
    path: Path,
    word: str,
):
    global _checked_words, _used, _table, _paths

    if i < 0 or i >= n or j < 0 or j >= n:
        return
    if _used[i][j]:
        return

    _used[i][j] = True
    word += _table[i][j]

    if word in words and len(word) > 1 and word not in _checked_words:
        _paths.append(path)
        _checked_words.add(word)

    if len(word) == MAX_WORD_LEN:
        return

    for d, (di, dj) in dirs:
        _dfs(i + di, j + dj, path=path.add(d), word=word)

    _used[i][j] = False


if __name__ == "__main__":
    search(["ьреот", "нпнар", "банка", "тиднф", "йнато"])
    for w in _checked_words:
        print(w)
