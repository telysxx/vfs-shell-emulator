"""Tests for the REPL logic and the script runner."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from shell import Shell
from vfs import VFS

EXAMPLES = Path(__file__).resolve().parent.parent / "vfs_examples"


def make_shell(prompt: str = "{vfs}:{cwd}$ ") -> Shell:
    """Create a shell on the minimal example VFS."""
    vfs = VFS.from_json(str(EXAMPLES / "minimal.json"))
    return Shell(vfs, prompt)


def capture(action) -> str:
    """Return everything that ``action`` prints."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        action()
    return buffer.getvalue()


class ShellTest(unittest.TestCase):
    """Behaviour of execute_line and run_script."""

    def test_prompt_contains_vfs_name_and_cwd(self):
        """The prompt template is filled with the VFS name and cwd."""
        self.assertEqual(make_shell().prompt, "minimal:/$ ")

    def test_unknown_command(self):
        """Unknown commands are reported and the shell goes on."""
        shell = make_shell()
        output = capture(lambda: shell.execute_line("frobnicate 1"))
        self.assertIn("unknown command: frobnicate", output)

    def test_exit_stops_the_shell(self):
        """exit returns False."""
        self.assertFalse(make_shell().execute_line("exit"))

    def test_blank_and_comment_lines(self):
        """Blank lines and comments do nothing."""
        shell = make_shell()
        output = capture(lambda: shell.execute_line("  # note"))
        self.assertEqual(output, "")
        self.assertTrue(shell.execute_line(""))

    def test_parse_error_is_reported(self):
        """An unbalanced quote does not crash the shell."""
        shell = make_shell()
        output = capture(lambda: shell.execute_line('ls "oops'))
        self.assertIn("Error", output)

    def test_script_echoes_input_and_output(self):
        """The script dialog shows prompts, commands and results."""
        shell = make_shell()
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "s.txt"
            script.write_text("# comment\npwd\nexit\npwd\n", encoding="utf-8")
            output = capture(lambda: shell.run_script(str(script)))
        self.assertIn("minimal:/$ pwd\n/\n", output)
        self.assertNotIn("# comment", output)
        self.assertEqual(output.count("minimal:/$ pwd"), 1)

    def test_missing_script(self):
        """A missing script raises OSError."""
        with self.assertRaises(OSError):
            make_shell().run_script("/no/such/script.txt")


if __name__ == "__main__":
    unittest.main()
