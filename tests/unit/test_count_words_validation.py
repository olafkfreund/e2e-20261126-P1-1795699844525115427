# Criterion (AC#1): count_words raises ValueError('min_len must be >= 1') for
# min_len < 1 and ValueError('top must be >= 0') for top < 0; top=0 returns an
# empty list.

import pytest

from wordfreq.cli import count_words

SAMPLE_TEXT = "the quick brown fox jumps over the lazy dog the fox"


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -10],
    ids=["min_len_zero", "min_len_minus_one", "min_len_minus_ten"],
)
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError, match=r"^min_len must be >= 1$"):
        count_words(SAMPLE_TEXT, min_len=min_len, top=10)


@pytest.mark.parametrize(
    "top",
    [-1, -5],
    ids=["top_minus_one", "top_minus_five"],
)
def test_count_words_top_negative_raises_value_error(top):
    with pytest.raises(ValueError, match=r"^top must be >= 0$"):
        count_words(SAMPLE_TEXT, min_len=1, top=top)


def test_count_words_top_zero_returns_empty_list():
    result = count_words(SAMPLE_TEXT, min_len=1, top=0)
    assert result == []
