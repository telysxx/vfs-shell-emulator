"""Tests for environment expansion and command parsing."""

import os
import unittest
from unittest import mock

from line_parser import expand_variables, parse_command


class ExpandVariablesTest(unittest.TestCase):
    """Expansion of $NAME and ${NAME}."""

    def test_plain_variable(self):
        """$NAME is replaced by its value."""
        self.assertEqual(expand_variables("ls $DIR", {"DIR": "/a"}), "ls /a")

    def test_braced_variable(self):
        """${NAME} can be glued to other text."""
        result = expand_variables("${DIR}/b", {"DIR": "/a"})
        self.assertEqual(result, "/a/b")

    def test_unknown_variable_is_empty(self):
        """Unknown variables expand to an empty string."""
        self.assertEqual(expand_variables("x$NOPE_X", {}), "x")

    def test_real_environment_is_used(self):
        """Without an explicit mapping os.environ is used."""
        with mock.patch.dict(os.environ, {"VFS_TEST_VAR": "42"}):
            self.assertEqual(expand_variables("$VFS_TEST_VAR"), "42")


class ParseCommandTest(unittest.TestCase):
    """Splitting a line into a command and arguments."""

    def test_split_and_quotes(self):
        """Quoted arguments stay together."""
        self.assertEqual(
            parse_command('cp "a b" c', {}), ["cp", "a b", "c"]
        )

    def test_comment_is_dropped(self):
        """Text after # is a comment."""
        self.assertEqual(parse_command("ls /  # list", {}), ["ls", "/"])

    def test_unbalanced_quote_raises(self):
        """A broken quote is reported as ValueError."""
        with self.assertRaises(ValueError):
            parse_command('ls "oops', {})


if __name__ == "__main__":
    unittest.main()
