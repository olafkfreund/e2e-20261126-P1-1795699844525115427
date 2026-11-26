"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_format_table_empty_input_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


# --- count_words: tie-breaking, case handling, filtering, slicing ---------------


def test_count_words_ties_sorted_alphabetically() -> None:
    assert count_words("zeta alpha mid beta") == [
        ("alpha", 1),
        ("beta", 1),
        ("mid", 1),
        ("zeta", 1),
    ]


def test_count_words_orders_by_count_then_word() -> None:
    assert count_words("b a a b c") == [("a", 2), ("b", 2), ("c", 1)]


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Hello HELLO hello") == [("hello", 3)]


def test_count_words_case_sensitive_keeps_original_case() -> None:
    # ASCII ordering puts uppercase before lowercase, so ties resolve that way.
    assert count_words("Hello HELLO hello", ignore_case=False) == [
        ("HELLO", 1),
        ("Hello", 1),
        ("hello", 1),
    ]


def test_count_words_case_sensitive_counts_variants_separately() -> None:
    assert count_words("Apple apple apple", ignore_case=False) == [
        ("apple", 2),
        ("Apple", 1),
    ]


def test_count_words_token_pattern_splits_on_punctuation() -> None:
    text = "don't stop-me_now 42 42"
    assert count_words(text) == [
        ("42", 2),
        ("don", 1),
        ("me", 1),
        ("now", 1),
        ("stop", 1),
        ("t", 1),
    ]


def test_count_words_ignores_non_ascii_letters() -> None:
    assert count_words("café naïve") == [("caf", 1), ("na", 1), ("ve", 1)]


def test_count_words_min_len_filters_short_words() -> None:
    assert count_words("a bb ccc bb", min_len=2) == [("bb", 2), ("ccc", 1)]


def test_count_words_top_keeps_most_frequent() -> None:
    assert count_words("a a b c", top=1) == [("a", 2)]


def test_count_words_top_zero_returns_empty() -> None:
    assert count_words("a a b", top=0) == []


def test_count_words_empty_text_returns_empty_list() -> None:
    assert count_words("") == []


def test_count_words_top_none_returns_all_words() -> None:
    assert count_words("a b c", top=None) == [("a", 1), ("b", 1), ("c", 1)]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"min_len": 0}, "min_len must be >= 1"),
        ({"min_len": -3}, "min_len must be >= 1"),
        ({"top": -1}, "top must be >= 0"),
    ],
)
def test_count_words_rejects_invalid_limits(
    kwargs: dict[str, int], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        count_words("a b", **kwargs)


# --- main: default stdin, --case-sensitive, output shape -----------------------


def test_cli_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("beta alpha beta\n"))
    rc = main([])
    assert rc == 0
    assert capsys.readouterr().out == "beta\t2\nalpha\t1\n"


def test_cli_dash_path_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("x y x\n"))
    rc = main(["-"])
    assert rc == 0
    assert capsys.readouterr().out == "x\t2\ny\t1\n"


def test_cli_tie_breaking_is_alphabetical(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "ties.txt"
    sample.write_text("pear apple", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t1\npear\t1\n"


def test_cli_lowercases_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple apple\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "apple\t3\n"


def test_cli_case_sensitive_preserves_case(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple apple\n"))
    assert main(["--case-sensitive"]) == 0
    assert capsys.readouterr().out == "apple\t2\nApple\t1\n"


def test_cli_tsv_output_ends_with_single_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("x y\n"))
    assert main([]) == 0
    out = capsys.readouterr().out
    assert out == "x\t1\ny\t1\n"
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_cli_empty_tsv_output_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_cli_top_zero_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b c\n"))
    assert main(["--top", "0"]) == 0
    assert capsys.readouterr().out == ""


def test_cli_json_output_ends_with_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a b c\n"))
    assert main(["--json", "--top", "2"]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert not out.endswith("\n\n")
    assert json.loads(out) == [
        {"word": "b", "count": 2},
        {"word": "a", "count": 1},
    ]


def test_cli_json_empty_input_emits_empty_array(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main(["--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


def test_cli_json_honors_case_sensitive(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple\n"))
    assert main(["--json", "--case-sensitive"]) == 0
    assert json.loads(capsys.readouterr().out) == [
        {"word": "Apple", "count": 1},
        {"word": "apple", "count": 1},
    ]


# --- argument validation and error exit codes ----------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["--min-len", "0"],
        ["--min-len", "-2"],
        ["--top", "-1"],
        ["--top", "abc"],
        ["--min-len", "x"],
        ["--no-such-flag"],
    ],
)
def test_cli_invalid_arguments_return_2_with_stderr(
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b\n"))
    rc = main(argv)
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err.strip() != ""
    assert captured.out == ""


def test_cli_missing_file_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.txt"
    rc = main([str(missing)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "does-not-exist.txt" in captured.err
    assert captured.out == ""


def test_cli_directory_path_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main([str(tmp_path)])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err.strip() != ""
    assert captured.out == ""


# --- python -m wordfreq ---------------------------------------------------------


def _run_module(*args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


def test_python_m_wordfreq_reads_stdin_by_default() -> None:
    result = _run_module("--top", "2", stdin="b a b c\n")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == "b\t2\na\t1\n"


def test_python_m_wordfreq_json_output_ends_with_newline() -> None:
    result = _run_module("--json", "--top", "2", stdin="b a b c\n")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.endswith("\n")
    assert json.loads(result.stdout) == [
        {"word": "b", "count": 2},
        {"word": "a", "count": 1},
    ]


def test_python_m_wordfreq_empty_tsv_writes_nothing() -> None:
    result = _run_module(stdin="")
    assert result.returncode == 0
    assert result.stdout == ""


def test_python_m_wordfreq_missing_file_returns_2(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    result = _run_module(str(missing))
    assert result.returncode == 2
    assert result.stderr.strip() != ""
    assert result.stdout == ""


def test_python_m_wordfreq_invalid_argument_returns_2() -> None:
    result = _run_module("--min-len", "0", stdin="a b\n")
    assert result.returncode == 2
    assert result.stderr.strip() != ""
