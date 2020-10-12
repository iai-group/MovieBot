from moviebot.utterance.utterance_user import UserUtterance

import pytest


@pytest.mark.parametrize('utterance, expected', [
    ('Hello WoRld', ['hello', 'world']),
    ('document.with, punctuation:   with?spaces\ttabs\nwith newlines\n\n\n',
     ['document', 'punctuation', 'space', 'tab', 'newlines']),
])
def test_process_text(utterance, expected):
    # Setup
    utterance = UserUtterance()

    # Exercise
    result = utterance.get_preprocessed_utterance(utterance)

    # Results
    assert result == expected

    # Cleanup - none