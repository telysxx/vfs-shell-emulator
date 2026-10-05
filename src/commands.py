"""Stub implementations of the emulator commands (stage 1)."""

from collections.abc import Callable


class CommandError(Exception):
    """Raised for invalid command arguments."""


def check_args(
    args: list[str], usage: str, minimum: int = 0, maximum: int | None = None
) -> None:
    """Raise CommandError unless ``minimum <= len(args) <= maximum``."""
    upper = minimum if maximum is None else maximum
    if not minimum <= len(args) <= upper:
        raise CommandError(f"Usage: {usage}")


def cmd_ls(args: list[str]) -> str:
    """Stub: print the command name and its arguments."""
    return " ".join(["ls", *args])


def cmd_cd(args: list[str]) -> str:
    """Stub: print the command name and its argument."""
    check_args(args, "cd [path]", 0, 1)
    return " ".join(["cd", *args])


CommandFunction = Callable[[list[str]], str]

COMMANDS: dict[str, CommandFunction] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
}
