"""Entry point of the VFS shell emulator (stage 1)."""

from shell import Shell

EXIT_OK = 0
EXIT_INTERRUPTED = 130


def main() -> int:
    """Start the interactive shell."""
    try:
        Shell().repl()
        return EXIT_OK
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return EXIT_INTERRUPTED


if __name__ == "__main__":
    raise SystemExit(main())
