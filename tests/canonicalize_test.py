from pathlib import Path

import tomlkit

from sbrunner_hooks.canonicalize import _canonicalize_pyproject


def test_canonicalize_pyproject_keeps_data_and_preserves_section_order(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[tool.ruff]
target-version = \"py310\"
line-length = 110

[project]
name = \"argocd-gs-scripts\"
dynamic = [\"dependencies\", \"version\"]

[tool.poetry]
version = \"0.0.0\"

[build-system]
requires = [\"poetry-core>=1.0.0\"]
build-backend = \"poetry.core.masonry.api\"
""",
        encoding="utf-8",
    )

    _canonicalize_pyproject(pyproject)

    content = pyproject.read_text(encoding="utf-8")
    doc = tomlkit.parse(content)

    assert doc["build-system"]["build-backend"] == "poetry.core.masonry.api"
    assert doc["project"]["name"] == "argocd-gs-scripts"
    assert doc["tool"]["ruff"]["target-version"] == "py310"
    assert doc["tool"]["poetry"]["version"] == "0.0.0"
    assert content.index("[tool.ruff]") < content.index("[tool.poetry]")
    assert content.index("[tool.poetry]") < content.index("[project]")
    assert content.index("[project]") < content.index("[build-system]")


def test_canonicalize_pyproject_reorders_top_level_and_tool_sections(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "argocd-gs-scripts"

[tool.poetry]
version = "0.0.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.abc]
foo = "bar"

[tool.ruff]
target-version = "py310"
line-length = 110
""",
        encoding="utf-8",
    )

    _canonicalize_pyproject(pyproject)

    content = pyproject.read_text(encoding="utf-8")

    assert content.index("[tool.ruff]") < content.index("[tool.abc]")
    assert content.index("[tool.abc]") < content.index("[tool.poetry]")
    assert content.index("[tool.poetry]") < content.index("[project]")
    assert content.index("[project]") < content.index("[build-system]")
