# Copyright (c) 2022-2023, Stéphane Brunner
"""Update the copyright header of the files."""

import argparse
import datetime
import os.path
import re
import subprocess  # nosec
import sys
from typing import Tuple

import yaml

CURRENT_YEAR = str(datetime.datetime.now().year)


def main() -> None:
    """Update the copyright header of the files."""
    args_parser = argparse.ArgumentParser("Update the copyright header of the files")
    args_parser.add_argument("--config", help="The configuration file", default=".github/copyright.yaml")
    args_parser.add_argument("--required", action="store_true", help="The copyright is required")
    args_parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    args_parser.add_argument("files", nargs=argparse.REMAINDER, help="The files to update")
    args = args_parser.parse_args()

    config = {}
    if os.path.exists(args.config):
        with open(args.config, encoding="utf-8") as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)

    one_date_re = re.compile(config.get("one_date_re", r" Copyright \(c\) (?P<year>[0-9]{4})"))
    tow_date_re = re.compile(
        config.get("tow_date_re", r" Copyright \(c\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})")
    )
    tow_date_format = config.get("tow_date_format", " Copyright (c) {from}-{to}")
    year_re = re.compile(r"^(?P<year>[0-9]{4})-")

    success = True
    no_git_log = False
    for file_name in args.files:
        try:
            status_str = subprocess.run(  # nosec
                ["git", "status", "--porcelain", "--", file_name],
                check=True,
                encoding="utf-8",
                stdout=subprocess.PIPE,
            ).stdout
            if status_str:
                used_year = CURRENT_YEAR

            date_str = subprocess.run(  # nosec
                ["git", "log", "--follow", "--pretty=format:%ci", "--", file_name],
                check=True,
                encoding="utf-8",
                stdout=subprocess.PIPE,
            ).stdout
            if not date_str:
                if args.verbose:
                    print(f"No log found with git on '{file_name}'.")
                else:
                    if not no_git_log:
                        print(f"No log found with git on '{file_name}' (the next messages will be hidden).")
                        no_git_log = True
                used_year = CURRENT_YEAR
            else:
                used_year_match = year_re.search(date_str)
                used_year = used_year_match.group("year")
        except FileNotFoundError:
            if not no_git_log:
                print("No Git found.")
                no_git_log = True
            used_year = CURRENT_YEAR
        except subprocess.CalledProcessError as error:
            print(f"Error with Git on '{file_name}' ({str(error)}).")
            used_year = CURRENT_YEAR

        with open(file_name, encoding="utf-8") as file_obj:
            content = file_obj.read()
            file_success, content = update_file(
                content,
                used_year,
                one_date_re,
                tow_date_re,
                tow_date_format,
                file_name,
                args.required,
                args.verbose,
            )
        if not file_success:
            success = False
            with open(file_name, "w", encoding="utf-8") as file_obj:
                file_obj.write(content)

    if not success:
        sys.exit(1)


def update_file(
    content: str,
    last_year: str,
    one_date_re: re.Match,
    tow_date_re: re.Match,
    tow_date_format: str,
    filename: str = "<unknown>",
    required: bool = False,
    verbose: bool = False,
) -> Tuple[bool, str]:
    """Update the copyright header of the file content."""
    tow_date_match = tow_date_re.search(content)
    if tow_date_match:
        if tow_date_match.group("to") == last_year:
            return True, content

        return False, tow_date_re.sub(
            tow_date_format.format(**{"from": tow_date_match.group("from"), "to": CURRENT_YEAR}), content
        )

    one_date_match = one_date_re.search(content)
    if one_date_match:
        copyright_year = one_date_match.group("year")

        if copyright_year == last_year:
            return True, content

        return False, one_date_re.sub(
            tow_date_format.format(**{"from": copyright_year, "to": CURRENT_YEAR}), content
        )

    if required or verbose:
        print(f"No copyright found on '{filename}'.")
    return not required, content


if __name__ == "__main__":
    main()
