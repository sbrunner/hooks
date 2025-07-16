import re

import pytest

from sbrunner_hooks.copyright import update_file


@pytest.mark.parametrize(
    ("content", "expected", "expected_updated", "required"),
    [
        ("toto", "toto", True, False),
        ("toto", "toto", False, True),
        ("# Test (c) 2023\ntoto", "# Test (c) 2023\ntoto", True, False),
        ("# Test (c) 2022\ntoto", "# Test (c) 2022-2024\ntoto", False, False),
        ("# Test (c) 2022-2023\ntoto", "# Test (c) 2022-2023\ntoto", True, False),
        ("# Test (c) 2021-2022\ntoto", "# Test (c) 2021-2024\ntoto", False, False),
        ("# Test (c) 2024-2024\ntoto", "# Test (c) 2024\ntoto", False, False),
        ("# Test (c) 2023-2023\ntoto", "# Test (c) 2023-2024\ntoto", False, False),
    ],
)
def test_update_file(content: str, expected: str, expected_updated: bool, required: bool) -> None:
    """Test the update_file function."""
    # The regexes are used to match the copyright line
    updated, content = update_file(
        content,
        "2023",
        re.compile(r" Test \(c\) (?P<year>[0-9]{4})"),
        re.compile(r" Test \(c\) (?P<from>[0-9]{4})-(?P<to>[0-9]{4})"),
        " Test (c) {year}",
        " Test (c) {from}-{to}",
        required=required,
        current_year="2024",
    )

    assert updated == expected_updated
    assert content == expected
