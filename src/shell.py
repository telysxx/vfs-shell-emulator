"""Interactive REPL and script runner of the shell emulator."""

from pathlib import Path

from commands import COMMANDS, CommandError, CommandFunction
from line_parser import parse_command

COMMENT_PREFIX = "#"
ROOT_PATH = "/"
EXIT_COMMAND = "exit"


class Shell:
    """A UNIX-like shell; commands are stubs at this stage."""

    def __init__(self, vfs_name: str, prompt_template: str):
        """Create a shell; the template may use ``{vfs}`` and ``{cwd}``."""
        self.vfs_name = vfs_name
        self.cwd = ROOT_PATH
        self.prompt_template = prompt_template

    @property
    def prompt(self) -> str:
        """Return the prompt with the VFS name and directory filled in."""
        return self.prompt_template.replace(
            "{vfs}", self.vfs_name
        ).replace("{cwd}", self.cwd)

    def execute_line(self, line: str) -> bool:
        """Execute one line; return False when the shell must exit."""
        try:
            parts = parse_command(line)
        except ValueError as exc:
            print(f"Error: cannot parse the command: {exc}")
            return True
        if not parts:
            return True
        command, args = parts[0], parts[1:]
        if command == EXIT_COMMAND:
            return False
        handler = COMMANDS.get(command)
        if handler is None:
            print(f"Error: unknown command: {command}")
            return True
        self._run_handler(handler, args)
        return True

    def _run_handler(self, handler: CommandFunction, args: list[str]) -> None:
        """Run a command and report its errors without stopping."""
        try:
            output = handler(args)
        except CommandError as exc:
            print(f"Error: {exc}")
            return
        if output:
            print(output)

    def run_script(self, script_path: str) -> bool:
        """Run a script, echoing every command like a live dialog.

        Empty lines and ``#`` comments are skipped. Returns False if the
        script executed ``exit``.
        """
        path = Path(script_path)
        if not path.is_file():
            raise OSError(f"Script not found: {script_path}")
        print(f"[script] {script_path}")
        with path.open("r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith(COMMENT_PREFIX):
                    continue
                print(f"{self.prompt}{line}")
                if not self.execute_line(line):
                    return False
        return True

    def repl(self) -> None:
        """Start the interactive command loop."""
        print("Type 'exit' to quit.")
        while True:
            try:
                line = input(self.prompt)
            except EOFError:
                print()
                break
            if not self.execute_line(line):
                break
