# Copyright (c) 2025, Stéphane Brunner

import argparse
import io
import re
from pathlib import Path
from typing import Any, AnyStr, Optional, Union

import multi_repo_automation as mra
import ruamel.yaml
import tomlkit


def _order_keys(
    data: dict[str, Any],
    first_keys: list[str],
    last_keys: Optional[list[str]] = None,
) -> ruamel.yaml.comments.CommentedMap:
    if last_keys is None:
        last_keys = []

    # use order: <first_keys>, <other>, <last_keys>
    new_data = [(key, data[key]) for key in first_keys if key in data]

    new_data += [e for e in data.items() if e[0] not in [*first_keys, *last_keys]]

    for key in last_keys:
        if key in data:
            new_data.append((key, data[key]))

    return ruamel.yaml.comments.CommentedMap(new_data)


def _order_sub_keys(
    data: Union[dict[str, dict[str, Any]], list[dict[str, AnyStr]]],
    first_keys: list[str],
    last_keys: Optional[list[str]] = None,
) -> None:
    items = data.items() if isinstance(data, dict) else enumerate(data)
    for key, value in items:
        # copy the last comment
        comment = None
        if hasattr(value, "ca"):
            last_value = list(value.values())[-1]
            if isinstance(last_value, dict) and hasattr(last_value, "ca"):
                last_last_key = list(last_value.keys())[-1]
                comment = last_value.ca.items.get(last_last_key)
                if comment is not None:
                    del last_value.ca.items[last_last_key]
            else:
                comment = value.ca.items.get(list(value.keys())[-1])  # type: ignore[union-attr]
        data[key] = _order_keys(value, first_keys, last_keys)  # type: ignore[index]
        if comment is not None:
            last_key = list(data[key].keys())[-1]  # type: ignore[index]
            if isinstance(data[key][last_key], ruamel.yaml.comments.CommentedMap):  # type: ignore[index]
                last_last_key = list(data[key][last_key].keys())[-1]  # type: ignore[union-attr,index]
                data[key][last_key].ca.items[last_last_key] = comment  # type: ignore[union-attr,index]
            else:
                data[key].ca.items[last_key] = comment  # type: ignore[union-attr,index]


def _canonicalize_workflow(workflow: mra.EditYAML) -> None:
    workflow.data = _order_keys(workflow.data, ["name", "on", "permissions", "env"], ["jobs"])

    # Add space after simple key
    for key in ["name"]:
        workflow.data.ca.items[key] = [
            None,
            None,
            ruamel.yaml.CommentToken("\n\n", ruamel.yaml.error.CommentMark(0), None),
            None,
        ]

    # add space after complex keys
    for key in ["on", "permissions", "env", "jobs"]:
        workflow.data.ca.items[key] = [
            None,
            [ruamel.yaml.CommentToken("\n", ruamel.yaml.error.CommentMark(0), None)],
            None,
            None,
        ]

    for name, job in workflow["jobs"].items():
        job = _order_keys(  # noqa: PLW2901
            job,
            ["name", "runs-on", "timeout-minutes", "if", "concurrency", "needs"],
            ["strategy", "env", "steps"],
        )
        workflow["jobs"][name] = job

        for key in reversed(["name", "runs-on", "timeout-minutes", "if", "concurrency", "needs"]):
            if key in job:
                job.ca.items[key] = [
                    None,
                    None,
                    ruamel.yaml.CommentToken("\n\n", ruamel.yaml.error.CommentMark(0), None),
                    None,
                ]
                break

        for key in reversed(["strategy", "env"]):
            if key in job:
                job.ca.items[key] = [
                    None,
                    None,
                    ruamel.yaml.CommentToken("\n\n", ruamel.yaml.error.CommentMark(0), None),
                    None,
                ]

    for job in workflow["jobs"].values():
        if "steps" in job:
            _order_sub_keys(job["steps"], ["name"], ["uses", "with", "run", "env", "if"])


def _canonicalize_prospector(prospector: mra.EditYAML) -> None:
    prospector.data = _order_keys(
        prospector.data,
        ["inherit"],
        [
            "pylint",
            "mypy",
            "bandit",
            "ruff",
            "pyflakes",
            "pycodestyle",
            "pydocstyle",
            "mccabe",
            "dodgy",
            "pyroma",
            "vulture",
            "frosted",
        ],
    )


def _split_pipe(exclude: str) -> list[str]:
    result = []
    in_parent = False
    file = ""

    for char in exclude:
        if char == "(":
            in_parent = True
        elif char == ")":
            in_parent = False
        elif char == "|" and not in_parent:
            result.append(file.strip())
            file = ""
        file += char

    result.append(file.strip())
    return result


_CLEAN_ENDLINE_RE = re.compile(r"\s*\n\s*")
_GET_START_END_RE = re.compile(r"([^(]*\()(.*)(\)[^)]*)")


def _canonicalize_pre_commit_exclude(exclude: str) -> Optional[ruamel.yaml.scalarstring.LiteralScalarString]:
    exclude = exclude.strip()
    if not exclude.startswith("(?x)"):
        return None
    exclude = exclude[4:]
    exclude = exclude.strip()
    exclude = _CLEAN_ENDLINE_RE.sub("", exclude)
    get_intro_end_match = _GET_START_END_RE.match(exclude)
    if get_intro_end_match is None:
        return None
    start, exclude, end = get_intro_end_match.groups()

    files = _split_pipe(exclude)

    return ruamel.yaml.scalarstring.LiteralScalarString(
        "\n".join(
            [
                f"(?x){start}",
                *[f"  {file}" for file in files],
                end,
            ],
        ),
    )


def _canonicalize_pre_commit(pre_commit_path: Path) -> None:
    with mra.EditYAML(pre_commit_path, run_pre_commit=False) as pre_commit_config:
        if "exclude" in pre_commit_config:
            exclude = _canonicalize_pre_commit_exclude(pre_commit_config["exclude"])
            if exclude is not None:
                pre_commit_config["exclude"] = exclude

        for repo in pre_commit_config["repos"]:
            for hook in repo["hooks"]:
                if "exclude" in hook:
                    exclude = _canonicalize_pre_commit_exclude(hook["exclude"])
                    if exclude is not None:
                        hook["exclude"] = exclude


def _canonicalize_pyproject(path: Path) -> None:
    with path.open() as f:
        doc = tomlkit.parse(f.read())

    new_doc = tomlkit.document()
    if "tool" not in new_doc:
        tool = doc["tool"]
        if isinstance(tool, tomlkit.items.Table) and "ruff" in tool:
            ruff = tool["ruff"]
            if isinstance(ruff, tomlkit.items.Table):
                new_doc["tool"] = {"ruff": ruff}
                if "lint" in ruff:
                    new_tool = new_doc["tool"]
                    assert isinstance(new_tool, tomlkit.items.Table)
                    new_ruff = new_tool["ruff"]
                    assert isinstance(new_ruff, tomlkit.items.Table)
                    new_ruff["lint"] = ruff["lint"]

    for key, value in doc.items():
        if key not in new_doc and key != "build-system":
            new_doc[key] = value
        elif key == "tool":
            for subkey, subvalue in value.items():
                new_tool = new_doc["tool"]
                assert isinstance(new_tool, tomlkit.items.Table)
                if subkey not in new_tool:
                    new_tool[subkey] = subvalue

    if "build-system" in doc:
        new_doc["build-system"] = doc["build-system"]

    # Remove double end of line
    out = io.StringIO()
    tomlkit.dump(new_doc, out, sort_keys=True)
    new_lines = []
    last_empty = False
    for line in out.getvalue().split("\n"):
        if line == "" and last_empty:
            continue
        if line == "":
            last_empty = True
            new_lines.append(line)
        else:
            last_empty = False
            new_lines.append(line)

    with path.open("w") as f:
        f.write("\n".join(new_lines))


def main() -> None:
    """Update the copyright header of the files."""
    args_parser = argparse.ArgumentParser("Format some files like the GitHub workflow")
    args_parser.add_argument("files", nargs=argparse.REMAINDER, type=Path, help="The files to update")
    args = args_parser.parse_args()

    for file_path in args.files:
        # is subpath of .github/workflows
        if file_path.parts[:3] == (".github", "workflows"):
            print(f"Format {file_path} as a GitHub workflow")
            with mra.EditYAML(file_path, run_pre_commit=False) as e:
                _canonicalize_workflow(e)

        elif (
            file_path.name in (".prospector.yaml", ".prospector.yml", "prospector.yaml", "prospector.yml")
            or file_path.name.startswith(".prospector-")
            or file_path.name.startswith("prospector-")
            or (len(file_path.parts) == 2 and file_path.parts[0].startswith("prospector_"))
        ):
            print(f"Format {file_path} as a Prospector configuration")
            with mra.EditYAML(file_path, run_pre_commit=False) as e:
                _canonicalize_prospector(e)

        elif file_path.name == "pyproject.toml":
            print(f"Format {file_path} as a pyproject.toml")
            _canonicalize_pyproject(file_path)

        elif file_path.name in (".pre-commit-config.yaml", ".pre-commit-config.yml"):
            print(f"Format {file_path} as a pre-commit configuration")
            _canonicalize_pre_commit(file_path)


if __name__ == "__main__":
    main()
