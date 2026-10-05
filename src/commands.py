"""Implementations of the emulator commands."""

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
    """List directory entries; directories get a trailing slash."""
    check_args(args, "ls [path]", 0, 1)
    path = args[0] if args else CURRENT_DIR
    entries = session.vfs.list_dir(path, session.cwd)
    return "  ".join(
        node.name + ("/" if node.is_dir else "") for node in entries
    )


def cmd_cd(session: Session, args: list[str]) -> str:
    """Change the current directory (no argument means the root)."""
    check_args(args, "cd [path]", 0, 1)
    path = args[0] if args else ROOT_PATH
    session.cwd = session.vfs.change_dir(path, session.cwd)
    return ""


def cmd_du(session: Session, args: list[str]) -> str:
    """Show the size in bytes of a path and of its subdirectories."""
    check_args(args, "du [path]", 0, 1)
    path = args[0] if args else CURRENT_DIR
    usage = session.vfs.disk_usage(path, session.cwd)
    return "\n".join(f"{size}\t{shown}" for size, shown in usage)


def cmd_cat(session: Session, args: list[str]) -> str:
    """Print the content of a file."""
    check_args(args, "cat <file>", 1)
    data = session.vfs.read_file(args[0], session.cwd)
    return data.decode("utf-8", errors="replace")


def cmd_find(session: Session, args: list[str]) -> str:
    """Find entries by exact name, starting from a directory."""
    check_args(args, "find [path] <name>", 1, 2)
    *head, name = args
    start = head[0] if head else CURRENT_DIR
    return "\n".join(session.vfs.find(start, name, session.cwd))


def cmd_rmdir(session: Session, args: list[str]) -> str:
    """Remove an empty directory."""
    check_args(args, "rmdir <empty-directory>", 1)
    session.vfs.remove_dir(args[0], session.cwd)
    return ""


def cmd_cp(session: Session, args: list[str]) -> str:
    """Copy a file or a directory inside the VFS."""
    check_args(args, "cp <source> <destination>", 2)
    session.vfs.copy(args[0], args[1], session.cwd)
    return ""


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
    "du": cmd_du,
    "cat": cmd_cat,
    "find": cmd_find,
    "rmdir": cmd_rmdir,
    "cp": cmd_cp,
    "tree": cmd_tree,
    "pwd": cmd_pwd,
}
