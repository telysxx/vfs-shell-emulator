"""Tests for the in-memory virtual file system."""

import unittest
from pathlib import Path

from vfs import VFS, VFSError

EXAMPLES = Path(__file__).resolve().parent.parent / "vfs_examples"


def load(name: str) -> VFS:
    """Load one of the example VFS files."""
    return VFS.from_json(str(EXAMPLES / f"{name}.json"))


class LoadingTest(unittest.TestCase):
    """Loading from JSON and path handling."""

    def test_name_comes_from_file(self):
        """The VFS name is the JSON file name without extension."""
        self.assertEqual(load("minimal").name, "minimal")

    def test_base64_is_decoded(self):
        """File content is stored as bytes."""
        vfs = load("multiple_files")
        node = vfs.resolve("/home/student/notes.txt")
        self.assertEqual(node.content, b"UNIX-like shell emulator\n")

    def test_normalize_relative_and_parent(self):
        """Dots and double dots are resolved inside the VFS."""
        vfs = load("multiple_files")
        result = vfs.normalize_path("../x", "/home/student")
        self.assertEqual(result, "/home/x")
        self.assertEqual(vfs.normalize_path("../../../..", "/a"), "/")

    def test_resolve_parent_of_cwd(self):
        """'..' is a real parent, not the current directory."""
        vfs = load("multiple_files")
        names = [n.name for n in vfs.list_dir("..", "/home/student")]
        self.assertEqual(names, ["student", "guest.txt"])

    def test_missing_path(self):
        """Unknown paths raise VFSError."""
        with self.assertRaises(VFSError):
            load("minimal").resolve("/nope")

    def test_tree_has_three_levels(self):
        """The deep example contains nested directories."""
        text = load("deep_tree").tree("/")
        self.assertIn("target.txt", text)
        self.assertEqual(text.splitlines()[0], "/")


class ReadOperationsTest(unittest.TestCase):
    """Read-only operations."""

    def setUp(self):
        """Load a VFS with several files."""
        self.vfs = load("multiple_files")

    def test_read_file(self):
        """File content is returned as bytes."""
        data = self.vfs.read_file("/home/student/data.txt")
        self.assertEqual(data, b"12345\n")

    def test_read_directory_fails(self):
        """A directory cannot be read as a file."""
        with self.assertRaises(VFSError):
            self.vfs.read_file("/home")

    def test_change_dir(self):
        """A valid directory gives its absolute path."""
        self.assertEqual(self.vfs.change_dir("student", "/home"),
                         "/home/student")

    def test_change_dir_to_file_fails(self):
        """cd into a file is an error."""
        with self.assertRaises(VFSError):
            self.vfs.change_dir("/home/guest.txt")

    def test_disk_usage(self):
        """Directories are listed first, the path itself is last."""
        usage = self.vfs.disk_usage("/home")
        self.assertEqual(usage[-1], (self.vfs.resolve("/home").size, "/home"))
        self.assertEqual(usage[0][1], "/home/student")

    def test_find(self):
        """Find returns absolute paths of exact matches."""
        self.assertEqual(
            self.vfs.find("/", "target.txt"),
            ["/docs/deep/level2/target.txt"],
        )


class ModificationTest(unittest.TestCase):
    """Operations that change the in-memory VFS."""

    def setUp(self):
        """Load a fresh VFS for every test."""
        self.vfs = load("multiple_files")

    def test_remove_empty_directory(self):
        """An empty directory disappears."""
        self.vfs.remove_dir("/empty")
        with self.assertRaises(VFSError):
            self.vfs.resolve("/empty")

    def test_remove_non_empty_fails(self):
        """A non-empty directory is protected."""
        with self.assertRaises(VFSError):
            self.vfs.remove_dir("/home")

    def test_remove_root_and_file_fail(self):
        """The root and plain files cannot be removed by rmdir."""
        with self.assertRaises(VFSError):
            self.vfs.remove_dir("/")
        with self.assertRaises(VFSError):
            self.vfs.remove_dir("/home/guest.txt")

    def test_remove_current_directory_fails(self):
        """The directory we are standing in cannot be removed."""
        with self.assertRaises(VFSError):
            self.vfs.remove_dir(".", "/empty")

    def test_copy_file_to_new_name(self):
        """A file is copied under a new name."""
        self.vfs.copy("/home/guest.txt", "/docs/guest_copy.txt")
        self.assertEqual(
            self.vfs.read_file("/docs/guest_copy.txt"), b"Guest file\n"
        )

    def test_copy_into_directory(self):
        """Copying to an existing directory keeps the file name."""
        self.vfs.copy("/home/guest.txt", "/empty")
        data = self.vfs.read_file("/empty/guest.txt")
        self.assertEqual(data, b"Guest file\n")

    def test_copy_directory_is_deep(self):
        """A copied directory is independent from the original."""
        self.vfs.copy("/docs", "/docs2")
        self.assertEqual(
            self.vfs.find("/docs2", "target.txt"),
            ["/docs2/deep/level2/target.txt"],
        )
        self.assertIsNot(
            self.vfs.resolve("/docs2/report.txt"),
            self.vfs.resolve("/docs/report.txt"),
        )

    def test_copy_errors(self):
        """Missing source, existing target and self-copy are rejected."""
        with self.assertRaises(VFSError):
            self.vfs.copy("/missing", "/x")
        with self.assertRaises(VFSError):
            self.vfs.copy("/home/guest.txt", "/etc/config.txt")
        with self.assertRaises(VFSError):
            self.vfs.copy("/docs", "/docs/deep/inside")
        with self.assertRaises(VFSError):
            self.vfs.copy("/", "/x")


if __name__ == "__main__":
    unittest.main()
