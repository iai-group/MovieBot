"""Tests for slot based recommender."""
from unittest import mock

import pytest

from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.slots import Slots
from moviebot.recommender.slot_based_recommender_model import (
    SlotBasedRecommenderModel,
)
from tests.mocks.mock_database import MockDataBase
from tests.mocks.mock_ontology import MockOntology


@pytest.fixture
@mock.patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def mock_dialogue_state() -> DialogueState:
    """Creates a mock representing agent_should_make_offer dialogue state."""

    class MockDialogueState(DialogueState):
        def _agent_offer_state(self) -> str:
            return str(["agent_should_make_offer"])

    dialogue_state = MockDialogueState(MockOntology(), [], isBot=False)
    dialogue_state.initialize()
    return dialogue_state


@pytest.fixture
@mock.patch("moviebot.database.database.DataBase", new=MockDataBase)
@mock.patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def slot_base_recommender() -> SlotBasedRecommenderModel:
    return SlotBasedRecommenderModel(MockDataBase(), MockOntology())


def test_recommend_items(
    mock_dialogue_state: DialogueState,
    slot_base_recommender: SlotBasedRecommenderModel,
) -> None:
    recommended_items = slot_base_recommender.recommend_items(
        mock_dialogue_state
    )
    assert len(recommended_items) == 3
    assert recommended_items == sorted(
        recommended_items,
        key=lambda item: item[Slots.RATING.value],
        reverse=True,
    )


def test_get_previous_recommend_items(
    mock_dialogue_state: DialogueState,
    slot_base_recommender: SlotBasedRecommenderModel,
) -> None:
    mock_dialogue_state.initialize()
    assert slot_base_recommender.get_previous_recommend_items() is None
    recommended_items = slot_base_recommender.recommend_items(
        mock_dialogue_state
    )
    assert (
        slot_base_recommender.get_previous_recommend_items()
        == recommended_items
    )
