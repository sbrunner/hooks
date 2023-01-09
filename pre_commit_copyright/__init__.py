import argparse
import datetime
import os.path
import re
from typing import Tuple

import yaml


def main() -> None:
    args_parser = argparse.ArgumentParser("Update the copyright header of the files")
    args_parser.add_argument("--config", help="The configuration file", default=".github/copyright.yaml")
    args_parser.add_argument("files", nargs=argparse.REMAINDER, help="The files to update")
    args = args_parser.parse_args()

    config = {}
    if os.path.exists(args.config):
        with open(args.config, encoding="utf-8") as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)

    one_date_re = re.compile(config.get("cone_date_re", r"^# Copyright \(c\) (<to>[0-9]{4})"))
    tow_date_re = re.compile(
        config.get("cone_date_re", r"^# Copyright \(c\) (<from>[0-9]{4})-(<to>[0-9]{4})")
    )
    one_date_format = config.get("one_date_format", "# Copyright (c) {to}")
    tow_date_format = config.get("one_date_format", "# Copyright (c) {from}-{to}")
    current_year = datetime.datetime.now().year

    for file_name in args.files:
        with open(file_name, encoding="utf-8") as file_obj:
            content = file_obj.read()
            updated, content = update_file(
                content, current_year, one_date_re, tow_date_re, one_date_format, tow_date_format
            )
        if updated:
            with open(file_name, "w", encoding="utf-8") as file_obj:
                file_obj.write(content)


def update_file(
    content: str,
    current_year: int,
    one_date_re: re.Match,
    tow_date_re: re.Match,
    one_date_format: str,
    tow_date_format: str,
) -> Tuple(bool, str):
    tow_date_match = tow_date_re.search(content)
    if tow_date_match:
        if tow_date_match.group("to") == current_year:
            return False, content

        return True, tow_date_re.sub(
            tow_date_format.format(**{"from": tow_date_match.group("from"), "to": current_year}), content
        )

    one_date_match = one_date_re.search(content)
    if one_date_match:
        to = one_date_match.group("to")

        if to == current_year:
            return False, content

        return True, one_date_re.sub(one_date_format.format(to=current_year), content)

    return False, content


if __name__ == "__main__":
    main()
