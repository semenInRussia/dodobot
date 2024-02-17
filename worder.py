from dataclasses import dataclass
from enum import Enum

n = 5
MAX_WORD_LEN = 5

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
_used: list[list[bool]] = [[False for _ in range(n)] for _ in range(n)]
_table: list[str] = []
_paths: list[Path] = []


def search(table: list[str], show=False) -> list[Path]:
    global _checked_words, _used, _table, _paths

    _checked_words = set()
    _paths = []
    _table = table

    for i in range(n):
        for j in range(n):
            path = Path(first=(i, j), rest=[])
            _fill_matrix(_used, False)
            _dfs(i, j, path=path, word="")

    if show:
        for w in _checked_words:
            print(w)
        nwords = len(_checked_words)
        print(f"I found {nwords} words")

    return _paths


def _dfs(i: int, j: int, path: Path, word: str):
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

    for d, (di, dj) in dirs:
        _dfs(i + di, j + dj, path=path.add(d), word=word)

    _used[i][j] = False


# inplace
def _fill_matrix(m: list[list], val):
    if not m:
        return

    for i in range(len(m)):
        for j in range(len(m[0])):
            m[i][j] = val


if __name__ == "__main__":
    tbl = ["бвгде", "ёзилм", "журка", "нопст", "фхцшщ"]
    path = Path(first=(0, 1), rest=[])
    search(tbl, show=True)
