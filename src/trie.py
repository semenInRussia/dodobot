from typing import Iterable, Iterator, Optional

class Trie:
    """The structure to store the list of strings.

    Idea is that root is empty strings, every node of this root is the
    first symbols of exists strings, their nodes are second
    characters.  So every node represents a string, if its field
    output is True, then this string is exists in the set"""
    arr: list["_Node"]
    size: int

    def __init__(self, _arr: Optional[Iterator[str]] = None) -> None:
        self.arr = [_Node()]
        self.size = 0
        if _arr is not None:
            for s in _arr:
                self.add(s)

    def add(self, s: str) -> None:
        """Add a string s to the set."""
        v = self._find_ptr(s, create=True)
        assert v is not None
        self.arr[v].is_end = True
        self.size += 1

    def update(self, strings: Iterable[str]) -> None:
        """Add all given strings to the set."""
        for s in strings:
            self.add(s)

    def remove(self, s: str) -> bool:
        """Remove the string s from the set.

        If string was inside set, return True, otherwise False"""
        v = self._find_ptr(s)
        if v is None or not self.arr[v].is_end:
            return False
        self.arr[v].is_end = False
        self.size -= 1
        return True

    def __contains__(self, s: str) -> bool:
        """Check that string s is exists in the set of strings of Trie."""
        v = self._find_ptr(s)
        return v is not None and self.arr[v].is_end

    def have_prefix(self, s: str) -> bool:
        """Check that string s is a prefix of any string in set."""
        return self._find_ptr(s) is not None

    def _find_ptr(self, s: str, create: bool = False) -> Optional[int]:
        """Return the index in self._arr to the string representation.

        If s is not found, return None.  If create is True, when find
        create the needed edges, so it creates the string and return
        index"""
        v: int = 0
        for ch in s:
            if ch not in self.arr[v].to:
                if create:
                    self.arr[v].to[ch] = len(self.arr)
                    self.arr.append(_Node())
                else:
                    return None
            v = self.arr[v].to[ch] or -1
        return v


    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[str]:
        return _dfs(self, 0, "")

def _dfs(t: Trie, v: int, s: str) -> Iterator[str]:
    if t.arr[v].is_end:
        yield s
    for ch, nod in t.arr[v].to.items():
        if nod is not None:
            yield from _dfs(t, nod, s + ch)


class _Node:
    """Every Optional integer represent the index of the node in the Trie.arr."""
    to: dict[str, Optional[int]]
    is_end: bool

    def __init__(self, is_end: bool = False):
        self.to = {}
        self.is_end = is_end

if __name__ == "__main__":
    t = Trie()
    t.add("bob")
    t.add("alice")
    t.add("back")
    assert "bob" in t
    assert t.have_prefix("bob")
    assert "bo" not in t
    assert t.have_prefix("bo")
    assert "back" in t
    assert t.have_prefix("back")
    assert "alice" in t
    assert t.have_prefix("alice")
    assert "a" not in t
    assert t.have_prefix("a")
    assert "y" not in t
    assert not t.have_prefix("y")
    assert len(t) == 3
    assert t.remove("back")
    assert len(t) == 2
    assert "back" not in t
    assert not t.remove("y")
    assert len(t) == 2
    assert "y" not in t
    print(list(t))
    print("Tests are passed!")
