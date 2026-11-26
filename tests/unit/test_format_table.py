# AC#2: format_table formats rows as word\tcount lines separated by \n and returns '' for empty input.

from wordfreq.cli import format_table


def test_format_table_two_rows_joined_with_newline_and_tab_separator_returns_expected_text():
    rows = [("the", 3), ("cat", 1)]

    result = format_table(rows)

    assert result == "the\t3\ncat\t1"


def test_format_table_rows_have_no_trailing_newline_returns_text_not_ending_with_newline():
    rows = [("alpha", 10), ("beta", 2)]

    result = format_table(rows)

    assert not result.endswith("\n")


def test_format_table_single_row_returns_word_tab_count_without_newline():
    rows = [("hello", 7)]

    result = format_table(rows)

    assert result == "hello\t7"


def test_format_table_empty_input_returns_empty_string():
    result = format_table([])

    assert result == ""
