"""In-memory virtual file system loaded from a JSON description."""

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT_PATH = "/"
SEPARATOR = "/"
KIND_DIR = "dir"
KIND_FILE = "file"
CURRENT_DIR = "."
PARENT_DIR = ".."
TREE_MID = "├── "
TREE_LAST = "└── "
TREE_PIPE = "│   "
TREE_GAP = "    "


class VFSError(Exception):
    """Raised when a VFS operation is invalid."""


@dataclass
class Node:
    """A file or a directory of the virtual file system."""

    name: str
    kind: str
    content: bytes = b""
    children: dict[str, "Node"] = field(default_factory=dict)

    @property
    def is_dir(self) -> bool:
        """Return True if the node is a directory."""
        return self.kind == KIND_DIR

    @property
    def size(self) -> int:
        """File size in bytes; a directory is the sum of its content."""
        if not self.is_dir:
            return len(self.content)
        return sum(child.size for child in self.children.values())


def join_path(parent: str, name: str) -> str:
    """Join an absolute directory path and an entry name."""
    return parent.rstrip(SEPARATOR) + SEPARATOR + name


class VFS:
    """A tree of files and directories that lives only in RAM."""

    def __init__(self, root: Node, name: str = "vfs"):
        """Create a VFS from a root directory node."""
        if not root.is_dir:
            raise VFSError("VFS root must be a directory.")
        self.root = root
        self.name = name

    @classmethod
    def from_json(cls, path: str) -> "VFS":
        """Load a VFS description from JSON; file data is Base64."""
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls(cls._node_from_dict(data), Path(path).stem)

    @classmethod
    def _node_from_dict(cls, data: dict) -> Node:
        """Build a node (recursively) from its JSON description."""
        if not isinstance(data, dict):
            raise VFSError("VFS node must be a JSON object.")
        kind = data.get("type")
        name = data.get("name", "")
        if kind == KIND_DIR:
            return cls._dir_from_dict(name, data)
        if kind == KIND_FILE:
            return cls._file_from_dict(name, data)
        raise VFSError(f"Unknown VFS node type: {kind!r}")

    @classmethod
    def _dir_from_dict(cls, name: str, data: dict) -> Node:
        """Build a directory node with all of its children."""
        node = Node(name=name, kind=KIND_DIR)
        for child_data in data.get("children", []):
            child = cls._node_from_dict(child_data)
            if not child.name or SEPARATOR in child.name:
                raise VFSError(f"Invalid VFS entry name: {child.name!r}")
            if child.name in node.children:
                raise VFSError(f"Duplicate VFS entry: {child.name}")
            node.children[child.name] = child
        return node

    @staticmethod
    def _file_from_dict(name: str, data: dict) -> Node:
        """Build a file node and decode its Base64 content."""
        encoded = data.get("content_base64", "")
        try:
            content = base64.b64decode(encoded, validate=True)
        except ValueError as exc:
            raise VFSError(f"Invalid base64 in file {name!r}.") from exc
        return Node(name=name, kind=KIND_FILE, content=content)

    def normalize_path(self, path: str, cwd: str = ROOT_PATH) -> str:
        """Return the canonical absolute form of a VFS path."""
        if not path.startswith(SEPARATOR):
            path = cwd + SEPARATOR + path
        parts: list[str] = []
        for part in path.split(SEPARATOR):
            if part in ("", CURRENT_DIR):
                continue
            if part == PARENT_DIR:
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return SEPARATOR + SEPARATOR.join(parts)

    def resolve(self, path: str, cwd: str = ROOT_PATH) -> Node:
        """Find the node that a path points to."""
        node = self.root
        normalized = self.normalize_path(path, cwd)
        for part in filter(None, normalized.split(SEPARATOR)):
            if not node.is_dir or part not in node.children:
                raise VFSError(f"No such file or directory: {path}")
            node = node.children[part]
        return node

    def list_dir(self, path: str = CURRENT_DIR, cwd: str = ROOT_PATH):
        """Return the entries of a directory (or the file itself)."""
        node = self.resolve(path, cwd)
        if not node.is_dir:
            return [node]
        return list(node.children.values())

    def tree(self, path: str = CURRENT_DIR, cwd: str = ROOT_PATH) -> str:
        """Return a ``tree``-like text representation of a subtree."""
        node = self.resolve(path, cwd)
        start = self.normalize_path(path, cwd)
        lines = [ROOT_PATH if start == ROOT_PATH else node.name]
        self._tree_lines(node, "", lines)
        return "\n".join(lines)

    def _tree_lines(self, node: Node, prefix: str, lines: list[str]) -> None:
        """Append the lines for all descendants of ``node``."""
        if not node.is_dir:
            return
        children = list(node.children.values())
        for child in children:
            is_last = child is children[-1]
            branch = TREE_LAST if is_last else TREE_MID
            suffix = SEPARATOR if child.is_dir else ""
            lines.append(f"{prefix}{branch}{child.name}{suffix}")
            extension = TREE_GAP if is_last else TREE_PIPE
            self._tree_lines(child, prefix + extension, lines)

    def read_file(self, path: str, cwd: str = ROOT_PATH) -> bytes:
        """Return the content of a file."""
        node = self.resolve(path, cwd)
        if node.is_dir:
            raise VFSError(f"Is a directory: {path}")
        return node.content

    def change_dir(self, path: str, cwd: str = ROOT_PATH) -> str:
        """Validate a directory and return its absolute path."""
        node = self.resolve(path, cwd)
        if not node.is_dir:
            raise VFSError(f"Not a directory: {path}")
        return self.normalize_path(path, cwd)

    def disk_usage(
        self, path: str = CURRENT_DIR, cwd: str = ROOT_PATH
    ) -> list[tuple[int, str]]:
        """Return (size, path) for every directory below ``path``.

        The requested path itself is always the last entry.
        """
        node = self.resolve(path, cwd)
        entries: list[tuple[int, str]] = []
        self._collect_usage(node, self.normalize_path(path, cwd), entries)
        return entries

    def _collect_usage(
        self, node: Node, path: str, entries: list[tuple[int, str]]
    ) -> None:
        """Collect sizes of subdirectories first, then of ``node``."""
        for child in node.children.values():
            if child.is_dir:
                self._collect_usage(child, join_path(path, child.name), entries)
        entries.append((node.size, path))

    def find(self, start: str, name: str, cwd: str = ROOT_PATH) -> list[str]:
        """Find all entries below ``start`` with exactly this name."""
        node = self.resolve(start, cwd)
        found: list[str] = []
        self._find_in(node, self.normalize_path(start, cwd), name, found)
        return found

    def _find_in(
        self, node: Node, path: str, name: str, found: list[str]
    ) -> None:
        """Walk a subtree and collect paths of matching entries."""
        if node.name == name:
            found.append(path)
        for child in node.children.values():
            self._find_in(child, join_path(path, child.name), name, found)
