import pytest

from moviebot.core.utterance.utterance import UserUtterance


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
    # Setup
    uu = UserUtterance(utterance)

    # Exercise
    result = uu.get_preprocessed_utterance()

    # Results
    assert result == expected

    # Cleanup - none
