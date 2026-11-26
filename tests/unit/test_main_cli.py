# AC#3: main reads stdin by default, honors flags, terminates output with final \n, returns 0
# (writes nothing for an empty TSV result).
import io
import json
import sys

import pytest

from wordfreq.cli import main


SAMPLE_TEXT = "the the the Cat cat dog a an"


@pytest.fixture
def stdin_text(monkeypatch):
    def _set(text):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))

    return _set


def _tsv_words(out):
    return [line.split("\t")[0] for line in out.splitlines() if line.strip()]


def test_main_reads_stdin_by_default_returns_zero(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    rc = main([])
    assert rc == 0


def test_main_reads_stdin_by_default_outputs_words(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main([])
    assert "dog" in _tsv_words(capsys.readouterr().out)


def test_main_dash_argument_reads_stdin(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main(["-"])
    assert "dog" in _tsv_words(capsys.readouterr().out)


def test_main_case_sensitive_flag_keeps_case_distinct(stdin_text, capsys):
    stdin_text("The the")
    main(["--case-sensitive"])
    words = _tsv_words(capsys.readouterr().out)
    assert {"The", "the"} <= set(words)


def test_main_top_flag_limits_rows_to_n(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main(["--top", "2"])
    assert len(_tsv_words(capsys.readouterr().out)) == 2


def test_main_min_len_flag_excludes_short_words(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main(["--min-len", "3"])
    words = _tsv_words(capsys.readouterr().out)
    assert "a" not in words and "an" not in words


def test_main_json_flag_outputs_valid_json(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main(["--json"])
    parsed = json.loads(capsys.readouterr().out)
    assert parsed is not None


def test_main_tsv_output_ends_with_newline(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main([])
    assert capsys.readouterr().out.endswith("\n")


def test_main_json_output_ends_with_newline(stdin_text, capsys):
    stdin_text(SAMPLE_TEXT)
    main(["--json"])
    assert capsys.readouterr().out.endswith("\n")


def test_main_empty_tsv_writes_nothing(stdin_text, capsys):
    stdin_text("")
    main([])
    assert capsys.readouterr().out == ""
