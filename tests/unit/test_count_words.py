# Criterion (AC#1): count_words extracts tokens, lowercases by default,
# preserves case with ignore_case=False, filters by min_len, and sorts
# by (-count, word).
import pytest

from wordfreq.cli import count_words


@pytest.mark.parametrize(
    "text,expected_words",
    [
        ("Hello, world! 42", {"hello", "world", "42"}),
        ("foo_bar-baz", {"foo", "bar", "baz"}),
        ("tab\tseparated\nlines", {"tab", "separated", "lines"}),
    ],
    ids=["punctuation_and_digits", "underscore_and_hyphen", "whitespace_kinds"],
)
def test_count_words_extracts_alphanumeric_tokens_only(text, expected_words):
    result = count_words(text)
    assert {word for word, _ in result} == expected_words


def test_count_words_lowercases_by_default():
    result = count_words("Python PYTHON python")
    assert result == [("python", 3)]


def test_count_words_preserves_case_when_ignore_case_false():
    result = count_words("Python PYTHON python", ignore_case=False)
    assert set(result) == {("Python", 1), ("PYTHON", 1), ("python", 1)}


def test_count_words_filters_words_shorter_than_min_len():
    result = count_words("a an the cat", min_len=3)
    assert {word for word, _ in result} == {"the", "cat"}


def test_count_words_keeps_word_equal_to_min_len():
    result = count_words("abc ab", min_len=3)
    assert {word for word, _ in result} == {"abc"}


def test_count_words_sorts_by_count_desc_then_word_asc():
    result = count_words("b a c c b b d")
    assert result == [("b", 3), ("c", 2), ("a", 1), ("d", 1)]
