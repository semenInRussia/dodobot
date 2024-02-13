from dataclasses import dataclass
from enum import Enum

n = 5
MAX_WORD_LEN = 6

words = set()

with open("words.txt", "r") as f:
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


def search(table: list[str]) -> list[str]:
    paths = []
    for i in range(n):
        for j in range(n):
            _dfs(
                table,
                paths,
                i,
                j,
                path=Path(first=(i, j), rest=[]),
                used=[[False] * n] * n,
                word="",
            )

    return paths


def _dfs(
    table: list[str],
    paths: list[Path],
    i: int,
    j: int,
    path: Path,
    used: list[list[bool]],
    word: str,
):
    if i < 0 or i >= n or j < 0 or j >= n:
        return
    if used[i][j]:
        return

    used[i][j] = True
    word += table[i][j]

    if word in words and len(word) > 1:
        paths.append(path)
        print("Yes", word)

    if len(word) == MAX_WORD_LEN:
        return

    for d, (di, dj) in dirs:
        _dfs(table, paths, i + di, j + dj, path.add(d), used, word)

    used[i][j] = False
