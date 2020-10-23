from moviebot.nlu.text_processing import TextProcess

import pytest


@pytest.mark.parametrize('utterance, expected', [
    ('Hello WoRld', ['hello', 'world']),
    ('document.with, punctuation:   with?spaces\ttabs\nwith newlines\n\n\n',
     ['document', 'punctuation', 'space', 'tab', 'newlines']),
])
def test_process_text(utterance, expected):
    # Setup
    tp = TextProcess()

    # Exercise
    result = tp.process_text(utterance)

    # Results
    assert result == expected

    # Cleanup - none