"""Check that the GitHub workflow has a timeout."""

import argparse
import sys
from pathlib import Path

import yaml


def main() -> None:
    """Check that the GitHub workflow has a timeout."""
    parser = argparse.ArgumentParser(description="""Check that the GitHub workflow has a timeout.""")
    parser.add_argument("files", nargs=argparse.REMAINDER, help="The files to check")
    args = parser.parse_args()

    success = True
    files = [Path(filename) for filename in args.files]
    if not files:
        files = [
            *Path(".").glob("github/workflows/*.yaml"),  # noqa: PTH201
            *Path().glob("github/workflows/*.yml"),
        ]
    for filename in files:
        with filename.open(encoding="utf-8") as open_file:
            workflow = yaml.load(open_file, Loader=yaml.SafeLoader)

        for name, job in workflow.get("jobs").items():
            if job.get("timeout-minutes") is None:
                print(f"The workflow '{filename}', job '{name}' has no timeout")
                success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
