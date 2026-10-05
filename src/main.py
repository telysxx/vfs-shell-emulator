"""Entry point of the VFS shell emulator (stage 2)."""

import argparse
import json
import os
import sys
from pathlib import Path

from config import build_config
from shell import Shell

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_INTERRUPTED = 130


def parse_cli(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line parameters; missing ones stay ``None``."""
    parser = argparse.ArgumentParser(
        description="UNIX-like shell emulator with an in-memory VFS"
    )
    parser.add_argument("--config", help="path to the JSON configuration")
    parser.add_argument("--vfs", help="path to the VFS JSON file")
    parser.add_argument("--prompt", help="REPL prompt ({vfs}, {cwd})")
    parser.add_argument("--script", help="path to the startup script")
    return parser.parse_args(argv)


def print_debug_config(config: dict) -> None:
    """Print all emulator parameters in a key=value form."""
    print("=== VFS emulator parameters ===")
    print(f"config_path    = {config['config_path'] or '<none>'}")
    print(f"vfs_path       = {config['vfs_path']}")
    print(f"prompt         = {config['prompt']!r}")
    print(f"startup_script = {config['startup_script'] or '<none>'}")
    print(f"cwd (real OS)  = {os.getcwd()}")
    print("===============================")


def main(argv: list[str] | None = None) -> int:
    """Load the configuration and the VFS, then run the shell."""
    try:
        config = build_config(parse_cli(argv))
        print_debug_config(config)
        vfs_name = Path(config["vfs_path"]).stem
        shell = Shell(vfs_name, config["prompt"])
        if config["startup_script"]:
            if not shell.run_script(config["startup_script"]):
                return EXIT_OK
        shell.repl()
        return EXIT_OK
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Startup error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return EXIT_INTERRUPTED


if __name__ == "__main__":
    raise SystemExit(main())
