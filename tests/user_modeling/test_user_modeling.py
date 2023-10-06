"""Tests for user modeling."""

import pytest

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.participant.participant import DialogueParticipant
from moviebot.core.intents.user_intents import UserIntents
from moviebot.nlu.recommendation_decision_processing import (
    RecommendationChoices,
    convert_choice_to_preference,
)
from moviebot.user_modeling.user_model import UserModel


@pytest.fixture
def user_model() -> UserModel:
    return UserModel()


def test_get_item_preferences(user_model: UserModel) -> None:
    """Tests get_item_preference."""
    preference = convert_choice_to_preference(RecommendationChoices.ACCEPT)
    user_model.item_preferences["movie1"] = preference
    preference = convert_choice_to_preference(RecommendationChoices.REJECT)
    user_model.item_preferences["movie2"] = preference

    assert user_model.get_item_preferences("movie1") == 1.0
    assert user_model.get_item_preferences("movie5") is None
    assert user_model.get_item_preferences() == {"movie1": 1.0, "movie2": -1.0}


def test_get_utterances_with_item_preferences(user_model: UserModel) -> None:
    """Tests get_utterances_with_item_preference."""
    user_model.item_preferences_nl["movie1"] = [
        AnnotatedUtterance(
            "I like movie1",
            DialogueParticipant.USER,
            intent=UserIntents.ACCEPT.value,
        ),
        AnnotatedUtterance(
            "Sounds good",
            DialogueParticipant.USER,
            intent=UserIntents.ACCEPT.value,
        ),
    ]

    assert user_model.get_utterances_with_item_preferences("movie1") == [
        AnnotatedUtterance(
            "I like movie1",
            DialogueParticipant.USER,
            intent=UserIntents.ACCEPT.value,
        ),
        AnnotatedUtterance(
            "Sounds good",
            DialogueParticipant.USER,
            intent=UserIntents.ACCEPT.value,
        ),
    ]
    assert user_model.get_utterances_with_item_preferences("movie2") == []


def test_get_slot_preferences(user_model: UserModel) -> None:
    """Tests get_slot_preference."""
    user_model.slot_preferences["genre"]["comedy"] = 1.0
    user_model.slot_preferences["genre"]["action"] = -1.0
    user_model.slot_preferences["genre"]["drama"] = -1.0

    assert user_model.get_slot_preferences("genre") == {
        "comedy": 1.0,
        "action": -1.0,
        "drama": -1.0,
    }
    assert user_model.get_slot_preferences() == {
        "genre": {"comedy": 1.0, "action": -1.0, "drama": -1.0}
    }
    assert user_model.get_slot_preferences("director") is None


def test_get_utterances_with_slot_preferences(user_model: UserModel) -> None:
    """Tests get_utterances_with_slot_preferences."""
    user_model.slot_preferences_nl["genre"]["action"] = [
        AnnotatedUtterance(
            "I don't like action",
            DialogueParticipant.USER,
            intent=UserIntents.REVEAL.value,
        ),
        AnnotatedUtterance(
            "I don't want to watch an action movie",
            DialogueParticipant.USER,
            intent=UserIntents.ACCEPT.value,
        ),
    ]

    assert user_model.get_utterances_with_slot_preferences("actors") == []
    assert (
        user_model.get_utterances_with_slot_preferences("genre", "comedy")
        == []
    )
    assert user_model.get_utterances_with_slot_preferences(
        "genre", "action"
    ) == [
        AnnotatedUtterance(
            "I don't like action",
            DialogueParticipant.USER,
            intent=UserIntents.REVEAL.value,
        ),
        AnnotatedUtterance(
            "I don't want to watch an action movie",
            DialogueParticipant.USER,
            intent=UserIntents.ACCEPT.value,
        ),
    ]
