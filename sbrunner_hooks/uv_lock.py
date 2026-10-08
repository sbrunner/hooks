# Copyright (c) 2026, Stéphane Brunner

"""Lock the Python requirements from a `.in` file with uv."""

import argparse
import subprocess  # nosec
import sys
import tempfile
from pathlib import Path


def locked_path(input_file: Path, extension: str) -> Path:
    """Get the path of the file generated from the input file."""
    return input_file.with_suffix(extension)


def build_command(input_file: Path, output_file: Path, python_version: str | None) -> list[str]:
    """
    Build the `uv pip compile` command.

    The header is disabled to keep the generated file reproducible from one machine to another.
    """
    command = ["uv", "pip", "compile", "--generate-hashes", "--no-header", "--quiet"]
    if python_version is not None:
        command.append(f"--python-version={python_version}")
    command.append(f"--output-file={output_file}")
    command.append(f"{input_file}")
    return command


def run_compile(input_file: Path, output_file: Path, python_version: str | None) -> bool:
    """Compile the input file into the output file, in the input file folder."""
    command = build_command(input_file, output_file, python_version)
    print(f"Run '{' '.join(command)}' in '{input_file.parent}'")
    proc = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603
        command,
        cwd=input_file.parent,
        check=False,
    )
    if proc.returncode != 0:
        print(f"Error: `uv pip compile` failed with the code {proc.returncode} on '{input_file}'")
        return False
    return True


def is_up_to_date(input_file: Path, output_file: Path, python_version: str | None) -> bool:
    """Check that the output file is up to date with the input file, without writing it."""
    if not output_file.exists():
        print(f"Error: the locked file '{output_file}' is missing, required by '{input_file}'")
        return False
    with tempfile.TemporaryDirectory() as tmp_dir:
        temporary = Path(tmp_dir) / output_file.name
        command = build_command(input_file, temporary, python_version)
        print(f"Run '{' '.join(command)}' in '{input_file.parent}'")
        proc = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603
            command,
            cwd=input_file.parent,
            check=False,
        )
        if proc.returncode != 0:
            print(f"Error: `uv pip compile` failed with the code {proc.returncode} on '{input_file}'")
            return False
        expected = temporary.read_bytes()
    if output_file.read_bytes() == expected:
        return True
    print(f"Error: the locked file '{output_file}' is not up to date with '{input_file}'")
    return False


def main() -> None:
    """Lock the Python requirements from a `.in` file with uv."""
    parser = argparse.ArgumentParser(
        description="""Lock the Python requirements from a `.in` file with uv.""",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check that the generated file is up to date, do not write it",
    )
    parser.add_argument(
        "--python-version",
        help="The Python version used to resolve the dependencies, e.g.: 3.14",
    )
    parser.add_argument(
        "--extension",
        default=".txt",
        help="The extension of the generated file, `.txt` by default",
    )
    parser.add_argument("files", nargs=argparse.REMAINDER, help="The `.in` files to lock")
    args = parser.parse_args()

    success = True
    for input_file in [Path(filename) for filename in args.files]:
        if input_file.suffix != ".in":
            print(f"Ignore '{input_file}', not a `.in` file")
            continue
        output_file = locked_path(input_file, args.extension)
        if args.check:
            success = is_up_to_date(input_file, output_file, args.python_version) and success
        else:
            success = run_compile(input_file, output_file, args.python_version) and success

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
