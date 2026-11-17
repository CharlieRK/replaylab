import subprocess
import sys

import pytest


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "replaylab", *args], capture_output=True, text=True
    )


def test_generate_and_validate(tmp_path):
    generated = run("generate", "--count", "50", "--seed", "7")
    assert generated.returncode == 0
    assert len(generated.stdout.splitlines()) == 50
    path = tmp_path / "quotes.jsonl"
    path.write_text(generated.stdout)
    validated = run("validate", str(path))
    assert validated.returncode == 0
    assert validated.stdout == "Validated 50 events\n"


@pytest.mark.parametrize("kind", ["gap", "duplicate", "reorder", "malformed"])
def test_bad_stream_reports_line(tmp_path, kind):
    lines = run("generate", "--count", "3").stdout.splitlines()
    lines = {
        "gap": [lines[0], lines[2]],
        "duplicate": [lines[0], lines[0]],
        "reorder": [lines[1], lines[0]],
        "malformed": [lines[0], "{}"],
    }[kind]
    path = tmp_path / "bad.jsonl"
    path.write_text("\n".join(lines) + "\n")
    result = run("validate", str(path))
    assert result.returncode == 2
    assert "line " in result.stderr


def test_invalid_count_and_missing_file():
    assert run("generate", "--count", "-1").returncode == 2
    assert run("validate", "/nonexistent/replaylab.jsonl").returncode == 2


def test_cli_without_path(monkeypatch):
    monkeypatch.setenv("PATH", "")
    result = run("generate", "--count", "2")
    assert result.returncode == 0, result.stderr
    assert len(result.stdout.splitlines()) == 2
