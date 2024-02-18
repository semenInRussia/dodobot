from dataclasses import dataclass

n = 5
MAX_WORD_LEN = 5

words = set()

with open("dict.txt", "r") as f:
    words = set(map(str.strip, f))


Point = tuple[int, int]

_deltas: list[Point] = [
    (-1, -1),
    (-1, 0),
    (-1, +1),
    (0, +1),
    (+1, +1),
    (+1, 0),
    (+1, -1),
    (0, -1),
]


@dataclass
class WordPath:
    first: Point
    rest: list[Point]

    def add(self, d: Point):
        return WordPath(first=self.first, rest=self.rest + [d])


_checked_words: set[str] = set()
_used: list[list[bool]] = [[False for _ in range(n)] for _ in range(n)]
_table: list[str] = []
_paths: list[WordPath] = []


def search(table: list[str], show=False) -> list[WordPath]:
    global _checked_words, _used, _table, _paths

    _checked_words = set()
    _paths = []
    _table = table

    for i in range(n):
        for j in range(n):
            path = WordPath(first=(i, j), rest=[])
            _fill_matrix(_used, False)
            _dfs(i, j, path=path, word="")

    if show:
        for w in _checked_words:
            print(w)
        nwords = len(_checked_words)
        print(f"I found {nwords} words")

    return _paths


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
