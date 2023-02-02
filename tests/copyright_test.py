import re

import pytest

from pre_commit_hooks.copyright import update_file


@pytest.mark.parametrize(
    "content,expected,expected_updated,required",
    [
        ("toto", "toto", True, False),
        ("toto", "toto", False, True),
        ("# Copyright (c) 2023\ntoto", "# Copyright (c) 2023\ntoto", True, False),
        ("# Copyright (c) 2022\ntoto", "# Copyright (c) 2022-2023\ntoto", False, False),
        ("# Copyright (c) 2022-2023\ntoto", "# Copyright (c) 2022-2023\ntoto", True, False),
        ("# Copyright (c) 2021-2022\ntoto", "# Copyright (c) 2021-2023\ntoto", False, False),
        ("# Copyright (c) 2023-2023\ntoto", "# Copyright (c) 2023\ntoto", False, False),
    ],
)
def test_update_file(content: str, expected: str, expected_updated: bool, required: bool):
    updated, content = update_file(
        content,
        "2023",
        re.compile(r" Copyright \(c\) (?P<year>[0-9]{4})"),
        re.compile(r" Copyright \(c\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})"),
        " Copyright (c) {year}",
        " Copyright (c) {from}-{to}",
        required=required,
    )

    assert updated == expected_updated
    assert content == expected
