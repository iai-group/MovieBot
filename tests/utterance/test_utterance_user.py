from typing import List

import pytest

from moviebot.core.utterance.utterance import UserUtterance
from moviebot.nlu.text_processing import Token


@pytest.mark.parametrize(
    "utterance, expected",
    [
        (
            "Hello WoRld",
            [
                Token("Hello", 0, lemma="hello"),
                Token("WoRld", 6, lemma="world"),
            ],
        ),
        (
            (
                "document.with, punctuation:   with?spaces\ttabs\nwith"
                " newlines\n\n\n"
            ),
            [
                Token("document", 0, 8, "document", False),
                Token("with", 9, 13, "with", True),
                Token("punctuation", 15, 26, "punctuation", False),
                Token("with", 30, 34, "with", True),
                Token("spaces", 35, 41, "space", False),
                Token("tabs", 42, 46, "tab", False),
                Token("with", 47, 51, "with", True),
                Token("newlines", 52, 60, "newlines", False),
            ],
        ),
    ],
)
def test_get_tokens(utterance: str, expected: List[Token]):
    uu = UserUtterance({"text": utterance})
    result = uu.get_tokens()

    assert result == expected
