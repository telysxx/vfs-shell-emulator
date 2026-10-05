"""Tests for the emulator commands working on a VFS."""

import unittest
from pathlib import Path

from commands import COMMANDS, CommandError, Session
from vfs import VFS, VFSError

EXAMPLES = Path(__file__).resolve().parent.parent / "vfs_examples"


def make_session() -> Session:
    """Create a session on the multi-file example VFS."""
    return Session(VFS.from_json(str(EXAMPLES / "multiple_files.json")))


def run(session: Session, command: str, *args: str) -> str:
    """Run a command by name and return its output."""
    return COMMANDS[command](session, list(args))


class CoreCommandsTest(unittest.TestCase):
    """ls, cd, du, cat, find."""

    def setUp(self):
        """Start every test in the root of a fresh VFS."""
        self.session = make_session()

    def test_ls_marks_directories(self):
        """Directories get a trailing slash."""
        self.assertEqual(
            run(self.session, "ls", "/home"), "student/  guest.txt"
        )

    def test_ls_parent_directory(self):
        """'ls ..' lists the parent, not the current directory."""
        run(self.session, "cd", "/home/student")
        self.assertEqual(run(self.session, "ls", ".."), "student/  guest.txt")

    def test_cd_relative_and_back(self):
        """cd works with relative paths, '..' and without arguments."""
        run(self.session, "cd", "home/student")
        self.assertEqual(self.session.cwd, "/home/student")
        run(self.session, "cd", "../..")
        self.assertEqual(self.session.cwd, "/")
        run(self.session, "cd", "/docs")
        run(self.session, "cd")
        self.assertEqual(self.session.cwd, "/")

    def test_cd_errors_keep_directory(self):
        """A failed cd does not move us."""
        with self.assertRaises(VFSError):
            run(self.session, "cd", "/nope")
        with self.assertRaises(VFSError):
            run(self.session, "cd", "/home/guest.txt")
        self.assertEqual(self.session.cwd, "/")

    def test_du(self):
        """du prints subdirectories first and the total last."""
        lines = run(self.session, "du", "/home").splitlines()
        self.assertEqual(lines, ["31\t/home/student", "42\t/home"])

    def test_cat(self):
        """cat prints the file content."""
        self.assertEqual(
            run(self.session, "cat", "/home/guest.txt"), "Guest file\n"
        )

    def test_cat_directory_fails(self):
        """cat refuses directories."""
        with self.assertRaises(VFSError):
            run(self.session, "cat", "/home")

    def test_find_with_and_without_path(self):
        """find accepts an optional start directory."""
        expected = "/docs/deep/level2/target.txt"
        self.assertEqual(run(self.session, "find", "target.txt"), expected)
        self.assertEqual(run(self.session, "find", "/docs", "target.txt"),
                         expected)
        self.assertEqual(run(self.session, "find", "/", "absent"), "")

    def test_wrong_argument_count(self):
        """Wrong arguments give a usage message."""
        for command, args in (
            ("ls", ["a", "b"]),
            ("cd", ["a", "b"]),
            ("du", ["a", "b"]),
            ("cat", []),
            ("find", []),
            ("find", ["a", "b", "c"]),
        ):
            with self.subTest(command=command, args=args):
                with self.assertRaises(CommandError):
                    COMMANDS[command](self.session, args)


if __name__ == "__main__":
    unittest.main()
