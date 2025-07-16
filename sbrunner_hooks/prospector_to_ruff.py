#!/usr/bin/env python3

# Get the Ruff configuration from the prospector.yaml and put it in the pyproject.toml

import argparse
from pathlib import Path

import prospector.profiles.profile
import tomlkit


def main() -> None:
    """Update pyproject.toml with Ruff configuration from prospector.yaml."""
    parser = argparse.ArgumentParser(
        description="Update pyproject.toml with Ruff configuration from prospector.yaml",
    )
    parser.add_argument(
        "prospector_config",
        type=Path,
        nargs="+",
        help="Path to the prospector.yaml file containing the Ruff configuration",
    )

    args = parser.parse_args()

    for prospector_config in args.prospector_config:
        if not prospector_config.is_file():
            print(f"File {prospector_config} does not exist")
            continue

        pyproject_path = prospector_config.parent / "pyproject.toml"
        if not pyproject_path.is_file():
            print(f"File {pyproject_path} does not exist")
            continue

        print(f"Processing {prospector_config} and updating {pyproject_path}")

        profile_path: list[Path] = []

        workdir = Path.cwd()

        profile_path.append(workdir)
        profile_path.append(prospector.profiles.profile.BUILTIN_PROFILE_PATH)

        print(f"Using profile path: {', '.join(str(p) for p in profile_path)}")

        profile = prospector.profiles.profile.ProspectorProfile.load(prospector_config.name, profile_path)

        with pyproject_path.open("r", encoding="utf-8") as pyproject_file:
            pyproject_doc = tomlkit.parse(pyproject_file.read())
        ruff_config = pyproject_doc.setdefault("tool", {}).setdefault("ruff", {})
        lint_config = ruff_config.setdefault("lint", {})

        top_level_properties = {
            "builtins",
            "cache-dir",
            "exclude",
            "extend",
            "extend-exclude",
            "extend-include",
            "fix",
            "fix-only",
            "force-exclude",
            "include",
            "indent-width",
            "line-length",
            "namespace-packages",
            "output-format",
            "per-file-target-version",
            "preview",
            "required-version",
            "respect-gitignore",
            "show-fixes",
            "src",
            "target-version",
            "unsafe-fixes",
        }

        for key, value in list(lint_config.items()):
            if not isinstance(value, tomlkit.items.Table):
                del lint_config[key]

        lint_config["select"] = sorted(profile.ruff.get("enable", []))  # pylint: disable=no-member
        lint_config["ignore"] = sorted(profile.ruff.get("disable", []))  # pylint: disable=no-member

        for option, value in profile.ruff.get("options", {}).items():  # pylint: disable=no-member
            current_config = ruff_config if option in top_level_properties else lint_config
            if isinstance(value, dict):
                # If the value is a dictionary, treat it as a set of boolean flags.
                # Extract the keys with truthy values and store them as a list in the Ruff configuration.
                current_config[option] = [k for k, v in value.items() if v]
            else:
                current_config[option] = value
        with pyproject_path.open("w", encoding="utf-8") as pyproject_file:
            tomlkit.dump(pyproject_doc, pyproject_file)


if __name__ == "__main__":
    main()
