"""Run a command in files folder."""

import argparse
import subprocess  # nosec
import sys
from pathlib import Path


def main() -> None:
    """Run a command in files folder."""
    parser = argparse.ArgumentParser(
        description="""Run a command in files folder.

    Example:
    pre-commit-run-in-dir --pass-filename --cmd cmd arg1 -aarg2 -a-arg -a--arg --files file1 dir/file2

    will be transform in:
    cmd arg1 arg2 -arg --arg  file1
    (cd dir && cmd arg1 arg2 -arg --arg file2
    """,
    )
    parser.add_argument("--fail-fast", action="store_true", help="Fail on the first error")
    parser.add_argument("--pass-filename", action="store_true", help="Pass the filename to the command")
    parser.add_argument("--check", nargs="+", help="The check command")
    parser.add_argument("--cmd", nargs="+", help="The command", required=True)
    parser.add_argument("-a", "--arg", "--args", nargs="+", help="The args", default=[])
    parser.add_argument("--files", nargs="+", help="The files", required=True)
    args = parser.parse_args()

    command = [*args.cmd, *args.arg]
    success = True
    for file_path in [Path(filename) for filename in args.files]:
        file_path = Path.cwd() / file_path  # noqa: PLW2901
        check_success = True
        if args.check:
            proc = subprocess.run(  # pylint: disable=subprocess-run-check # nosec
                args.check,
                cwd=file_path.parent,
                check=False,
            )
            if proc.returncode != 0:
                if args.fail_fast:
                    sys.exit(proc.returncode)
                check_success = False
        else:
            check_success = False
        if not check_success:
            proc = subprocess.run(  # pylint: disable=subprocess-run-check # nosec
                [*command, file_path.name] if args.pass_filename else command,
                cwd=file_path.parent,
                check=False,
            )
            if proc.returncode != 0:
                if args.fail_fast:
                    sys.exit(proc.returncode)
                success = False
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
