# AC#3: return 2 with non-empty stderr on invalid arguments or missing files.
# Criterion: `main` and `python -m wordfreq` return `0` on success or `2` with
# non-empty `stderr` on invalid arguments or missing files.

import pytest

from wordfreq.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "-1"],
        ["--top", "abc"],
        ["--top", "1.5"],
        ["--min-len", "0"],
        ["--min-len", "abc"],
        ["--min-len", "2.5"],
    ],
    ids=[
        "top-negative-one",
        "top-non-integer-word",
        "top-float",
        "min-len-zero",
        "min-len-non-integer-word",
        "min-len-float",
    ],
)
def test_main_invalid_top_or_min_len_returns_two(argv, capsys):
    exit_code = main(argv)
    assert exit_code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "-1"],
        ["--top", "abc"],
        ["--top", "1.5"],
        ["--min-len", "0"],
        ["--min-len", "abc"],
        ["--min-len", "2.5"],
    ],
    ids=[
        "top-negative-one",
        "top-non-integer-word",
        "top-float",
        "min-len-zero",
        "min-len-non-integer-word",
        "min-len-float",
    ],
)
def test_main_invalid_top_or_min_len_writes_stderr(argv, capsys):
    main(argv)
    captured = capsys.readouterr()
    assert captured.err != ""


def test_main_unknown_option_returns_two(capsys):
    exit_code = main(["--no-such-option"])
    assert exit_code == 2


def test_main_unknown_option_writes_stderr(capsys):
    main(["--no-such-option"])
    captured = capsys.readouterr()
    assert captured.err != ""


def test_main_missing_file_returns_two(tmp_path, capsys):
    missing = tmp_path / "does-not-exist.txt"
    exit_code = main([str(missing)])
    assert exit_code == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does-not-exist.txt"
    main([str(missing)])
    captured = capsys.readouterr()
    assert captured.err != ""
