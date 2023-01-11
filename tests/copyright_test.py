import re

import pytest

from pre_commit_copyright import update_file


@pytest.mark.parametrize(
    "content,current_year,expected,expected_updated",
    [
        ("toto", "2023", "toto", False),
        ("# Copyright (c) 2023\ntoto", "2023", "# Copyright (c) 2023\ntoto", False),
        ("# Copyright (c) 2022\ntoto", "2023", "# Copyright (c) 2022-2023\ntoto", True),
        ("# Copyright (c) 2022-2023\ntoto", "2023", "# Copyright (c) 2022-2023\ntoto", False),
        ("# Copyright (c) 2021-2022\ntoto", "2023", "# Copyright (c) 2021-2023\ntoto", True),
    ],
)
def test_update_file(content: str, current_year: str, expected: str, expected_updated: bool):
    updated, content = update_file(
        content,
        current_year,
        re.compile(r"^# Copyright \(c\) (?P<year>[0-9]{4})"),
        re.compile(r"^# Copyright \(c\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})"),
        "# Copyright (c) {from}-{to}",
    )

    assert updated == expected_updated
    assert content == expected
