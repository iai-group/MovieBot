from moviebot.nlu.user_intents_checker import UserIntentsChecker
from tests.mocks.mock_data_loader import MockDataLoader

from unittest.mock import patch
import pytest

# global setup
config = {
    "ontology": "",
    "database": "",
    "slot_values_path": "",
    "tag_words_slots_path": "",
}


@pytest.mark.parametrize(
    "utterance",
    [
        "hello",
        "hi do you know of any interesting movies",
        "hey hey",
    ],
)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def test_check_hi_intent(utterance):
    # Setup
    uic = UserIntentsChecker(config)

    # Exercise
    result = uic.check_hi_intent(utterance)

    # Results
    assert len(result) == 1
    assert result[0].intent.name == "HI"

    # Cleanup - none


@pytest.mark.parametrize(
    "utterance",
    [
        "",
        "i would like to watch an action movie",
        "im interested in something like othello",
        "im interested in something like hi cousin",
    ],
)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def test_check_hi_intent_empty(utterance):
    # Setup
    uic = UserIntentsChecker(config)

    # Exercise
    result = uic.check_hi_intent(utterance)

    # Results
    assert len(result) == 0

    # Cleanup - none


@pytest.mark.parametrize(
    "utterance",
    [
        "im happy with my result bye",
        "exit",
        "i quit",
    ],
)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def test_check_bye_intent(utterance):
    # Setup
    uic = UserIntentsChecker(config)

    # Exercise
    result = uic.check_bye_intent(utterance)

    # Results
    assert len(result) == 1
    assert result[0].intent.name == "BYE"

    # Cleanup - none


@pytest.mark.parametrize(
    "utterance",
    [
        "",
        "hi",
        "i would like to watch an action movie",
        "im interested in something like bye bye birdie",
    ],
)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def test_check_bye_intent_empty(utterance):
    # Setup
    uic = UserIntentsChecker(config)

    # Exercise
    result = uic.check_bye_intent(utterance)

    # Results
    assert len(result) == 0

    # Cleanup - none
