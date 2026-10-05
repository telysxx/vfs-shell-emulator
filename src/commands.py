"""Emulator commands (stage 3: ls and cd are still stubs)."""

from collections.abc import Callable
from dataclasses import dataclass

from vfs import CURRENT_DIR, ROOT_PATH, VFS


class CommandError(Exception):
    """Raised for invalid command arguments."""


@dataclass
class Session:
    """State shared by commands: the VFS and the current directory."""

    vfs: VFS
    cwd: str = ROOT_PATH


def check_args(
    args: list[str], usage: str, minimum: int = 0, maximum: int | None = None
) -> None:
    """Raise CommandError unless ``minimum <= len(args) <= maximum``."""
    upper = minimum if maximum is None else maximum
    if not minimum <= len(args) <= upper:
        raise CommandError(f"Usage: {usage}")


def cmd_ls(session: Session, args: list[str]) -> str:
    """Stub: print the command name and its arguments."""
    return " ".join(["ls", *args])


def cmd_cd(session: Session, args: list[str]) -> str:
    """Stub: print the command name and its argument."""
    check_args(args, "cd [path]", 0, 1)
    return " ".join(["cd", *args])


def cmd_tree(session: Session, args: list[str]) -> str:
    """Print a subtree (service command, handy for demonstrations)."""
    check_args(args, "tree [path]", 0, 1)
    path = args[0] if args else CURRENT_DIR
    return session.vfs.tree(path, session.cwd)


def cmd_pwd(session: Session, args: list[str]) -> str:
    """Print the current directory (service command)."""
    check_args(args, "pwd")
    return session.cwd


CommandFunction = Callable[[Session, list[str]], str]

COMMANDS: dict[str, CommandFunction] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "tree": cmd_tree,
    "pwd": cmd_pwd,
}
