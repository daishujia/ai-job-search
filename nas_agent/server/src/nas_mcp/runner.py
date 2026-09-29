"""Detached runner: `python -m nas_mcp.runner EXITFILE -- cmd...` records the exit code when done."""
import subprocess
import sys
from pathlib import Path


def main() -> None:
    exitfile, sep, *cmd = sys.argv[1:]
    assert sep == "--" and cmd
    rc = subprocess.call(cmd)
    Path(exitfile).write_text(str(rc))
    sys.exit(rc)


if __name__ == "__main__":
    main()
