"""Command-line parsing and environment-variable expansion."""

import os
import re
import shlex
from collections.abc import Mapping

VARIABLE_PATTERN = re.compile(r"\$(\w+|\{[^}]+\})")


def expand_variables(text: str, env: Mapping[str, str] | None = None) -> str:
    """Expand ``$NAME`` and ``${NAME}`` using the real OS environment.

    Unknown variables expand to an empty string, like in a UNIX shell.
    """
    source = os.environ if env is None else env

    def replace(match: re.Match[str]) -> str:
        """Return the value of the variable found by the regex."""
        token = match.group(1)
        name = token[1:-1] if token.startswith("{") else token
        return source.get(name, "")

    return VARIABLE_PATTERN.sub(replace, text)


def parse_command(
    line: str, env: Mapping[str, str] | None = None
) -> list[str]:
    """Expand variables and split the line into command and arguments.

    Quotes are supported; text after an unquoted ``#`` is a comment.
    """
    return shlex.split(expand_variables(line, env), comments=True)
