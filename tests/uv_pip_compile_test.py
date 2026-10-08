# Copyright (c) 2026, Stéphane Brunner

"""Tests of the uv pip compile hook."""

import subprocess
import sys
from pathlib import Path

import pytest

from sbrunner_hooks import uv_pip_compile


def _output_of(command):
    return next(arg for arg in command if arg.startswith("--output-file=")).split("=", 1)[1]


def _fake_run(content, calls=None):
    def run(command, cwd=None, check=False):
        if calls is not None:
            calls.append({"command": command, "cwd": cwd})
        Path(_output_of(command)).write_text(content, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    return run


def test_compiled_path():
    assert uv_pip_compile.compiled_path(Path("ci/publish-requirements.in"), ".txt") == Path(
        "ci/publish-requirements.txt"
    )


def test_build_command_without_python_version():
    assert uv_pip_compile.build_command(Path("ci/a.in"), Path("ci/a.txt"), None, True, False) == [
        "uv",
        "pip",
        "compile",
        "--quiet",
        "--generate-hashes",
        "--no-header",
        "--output-file=ci/a.txt",
        "ci/a.in",
    ]


def test_build_command_with_python_version():
    command = uv_pip_compile.build_command(
        Path("/work/ci/a.in"), Path("/tmp/tmpdir/a.txt"), "3.14", True, False
    )
    assert command[6] == "--python-version=3.14"
    assert command[-2] == "--output-file=/tmp/tmpdir/a.txt"
    assert command[-1] == "/work/ci/a.in"


def test_build_command_without_hashes_and_with_header():
    command = uv_pip_compile.build_command(Path("ci/a.in"), Path("ci/a.txt"), None, False, True)
    assert "--generate-hashes" not in command
    assert "--no-header" not in command


def test_run_compile(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(uv_pip_compile.subprocess, "run", _fake_run("locked\n", calls))
    input_file = tmp_path / "requirements.in"
    input_file.write_text("tag-publish[docker]==1.3.0\n", encoding="utf-8")

    assert uv_pip_compile.run_compile(input_file, tmp_path / "requirements.txt", "3.14", True, False) is True
    assert (tmp_path / "requirements.txt").read_text(encoding="utf-8") == "locked\n"
    assert calls[0]["cwd"] == tmp_path
    assert "--python-version=3.14" in calls[0]["command"]


def test_run_compile_in_error(monkeypatch, tmp_path):
    monkeypatch.setattr(
        uv_pip_compile.subprocess,
        "run",
        lambda command, cwd=None, check=False: subprocess.CompletedProcess(command, 1),
    )
    input_file = tmp_path / "requirements.in"
    input_file.write_text("tag-publish[docker]==1.3.0\n", encoding="utf-8")

    assert uv_pip_compile.run_compile(input_file, tmp_path / "requirements.txt", None, True, False) is False


def test_main_ignores_the_other_files(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", ["uv-pip-compile", str(tmp_path / "requirements.txt")])

    uv_pip_compile.main()

    assert "Ignore" in capsys.readouterr().out


def test_main_compiles(monkeypatch, tmp_path):
    monkeypatch.setattr(uv_pip_compile.subprocess, "run", _fake_run("locked\n"))
    input_file = tmp_path / "publish-requirements.in"
    input_file.write_text("tag-publish[docker]==1.3.0\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["uv-pip-compile", "--python-version=3.14", str(input_file)])

    uv_pip_compile.main()

    assert (tmp_path / "publish-requirements.txt").read_text(encoding="utf-8") == "locked\n"


def test_main_with_an_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(uv_pip_compile.subprocess, "run", _fake_run("locked\n"))
    input_file = tmp_path / "publish-requirements.in"
    input_file.write_text("tag-publish[docker]==1.3.0\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["uv-pip-compile", "--extension=.pip", "--no-hashes", "--header", str(input_file)],
    )

    uv_pip_compile.main()

    assert (tmp_path / "publish-requirements.pip").read_text(encoding="utf-8") == "locked\n"


def test_main_fails_when_the_compilation_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(
        uv_pip_compile.subprocess,
        "run",
        lambda command, cwd=None, check=False: subprocess.CompletedProcess(command, 1),
    )
    input_file = tmp_path / "publish-requirements.in"
    input_file.write_text("tag-publish[docker]==1.3.0\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["uv-pip-compile", str(input_file)])

    with pytest.raises(SystemExit) as exc_info:
        uv_pip_compile.main()

    assert exc_info.value.code == 1
