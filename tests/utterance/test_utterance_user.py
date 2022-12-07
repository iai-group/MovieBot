import pytest

from moviebot.core.shared.utterance.utterance import UserUtterance


@pytest.mark.parametrize(
    "utterance, expected",
    [
        ("Hello WoRld", ["hello", "world"]),
        (
            (
                "document.with, punctuation:   with?spaces\ttabs\nwith"
                " newlines\n\n\n"
            ),
            ["document", "punctuation", "space", "tab", "newlines"],
        ),
    ],
)
def test_get_processed_utterance(utterance, expected):
    uu = UserUtterance(utterance)
    result = uu.get_preprocessed_utterance()

    assert result == expected
