# Copyright (c) 2026, Stéphane Brunner

"""Tests of the run-in-dir helper."""

import subprocess
import sys

import pytest

from sbrunner_hooks import run_in_dir


class Recorder:
    """Record the subprocess calls and return a fixed code."""

    def __init__(self, returncode=0):
        self.calls = []
        self.returncode = returncode

    def run(self, command, cwd=None, check=False):
        self.calls.append({"command": command, "cwd": cwd})
        return subprocess.CompletedProcess(command, self.returncode)

    @property
    def commands(self):
        return [call["command"] for call in self.calls]


def test_several_args_are_all_passed(monkeypatch, tmp_path):
    recorder = Recorder()
    monkeypatch.setattr(run_in_dir.subprocess, "run", recorder.run)
    (tmp_path / "uv.lock").write_text("lock\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run-in-dir",
            "--cmd",
            "uv",
            "export",
            "-a--format=pylock.toml",
            "-a--output-file=pylock.toml",
            "--files",
            str(tmp_path / "uv.lock"),
        ],
    )

    run_in_dir.main()

    assert recorder.commands == [["uv", "export", "--format=pylock.toml", "--output-file=pylock.toml"]]
    assert recorder.calls[0]["cwd"] == tmp_path


def test_pass_filename(monkeypatch, tmp_path):
    recorder = Recorder()
    monkeypatch.setattr(run_in_dir.subprocess, "run", recorder.run)
    (tmp_path / "Pipfile").write_text("[packages]\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["run-in-dir", "--pass-filename", "--cmd", "cat", "--files", str(tmp_path / "Pipfile")],
    )

    run_in_dir.main()

    assert recorder.commands == [["cat", "Pipfile"]]


def test_the_command_is_not_run_when_the_check_succeeds(monkeypatch, tmp_path):
    recorder = Recorder()
    monkeypatch.setattr(run_in_dir.subprocess, "run", recorder.run)
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run-in-dir",
            "--check",
            "poetry",
            "check",
            "--cmd",
            "poetry",
            "lock",
            "--files",
            str(tmp_path / "pyproject.toml"),
        ],
    )

    run_in_dir.main()

    assert recorder.commands == [["poetry", "check"]]


def test_the_command_is_run_when_the_check_fails(monkeypatch, tmp_path):
    calls = []

    def run(command, cwd=None, check=False):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1 if command == ["poetry", "check"] else 0)

    monkeypatch.setattr(run_in_dir.subprocess, "run", run)
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run-in-dir",
            "--check",
            "poetry",
            "check",
            "--cmd",
            "poetry",
            "lock",
            "--files",
            str(tmp_path / "pyproject.toml"),
        ],
    )

    run_in_dir.main()

    assert calls == [["poetry", "check"], ["poetry", "lock"]]


def test_error_on_a_failing_command(monkeypatch, tmp_path):
    recorder = Recorder(returncode=2)
    monkeypatch.setattr(run_in_dir.subprocess, "run", recorder.run)
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["run-in-dir", "--cmd", "uv", "lock", "--files", str(tmp_path / "pyproject.toml")],
    )

    with pytest.raises(SystemExit) as exc_info:
        run_in_dir.main()

    assert exc_info.value.code == 1
