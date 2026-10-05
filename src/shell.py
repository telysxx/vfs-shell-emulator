"""Interactive REPL of the shell emulator (stage 1)."""

from commands import COMMANDS, CommandError, CommandFunction
from line_parser import parse_command

DEFAULT_PROMPT = "VFS> "
EXIT_COMMAND = "exit"


class Shell:
    """A UNIX-like shell; commands are stubs at this stage."""

    def __init__(self, prompt: str = DEFAULT_PROMPT):
        """Create a shell with the given prompt."""
        self.prompt = prompt

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
