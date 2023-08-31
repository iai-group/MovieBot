"""Tests for slot based recommender."""
from unittest import mock

import pytest

from moviebot.database.db_movies import DataBase
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.domain.movie_domain import MovieDomain
from moviebot.recommender.slot_based_recommender_model import (
    SlotBasedRecommenderModel,
)


@pytest.fixture
def mock_dialogue_state() -> DialogueState:
    """Creates a mock representing agent_should_make_offer dialogue state."""

    class MockDialogueState(DialogueState):
        def _agent_offer_state(self) -> str:
            return str(["agent_should_make_offer"])

    dialogue_state = MockDialogueState(
        MovieDomain("tests/data/test_domain.yaml"), [], isBot=False
    )
    dialogue_state.initialize()
    return dialogue_state


@pytest.fixture
@mock.patch.object(DataBase, "_initialize_sql")
def slot_base_recommender(
    mock___initialize_sql: mock.MagicMock,
) -> SlotBasedRecommenderModel:
    return SlotBasedRecommenderModel(
        DataBase(None), MovieDomain("tests/data/test_domain.yaml")
    )


@mock.patch.object(
    DataBase, "database_lookup", return_value=[{"movie-001": "description"}]
)
def test_recommend_items(
    mock_database_lookup: mock.MagicMock,
    mock_dialogue_state: DialogueState,
    slot_base_recommender: SlotBasedRecommenderModel,
) -> None:
    recommended_items = slot_base_recommender.recommend_items(
        mock_dialogue_state
    )
    mock_database_lookup.assert_called_once()
    assert recommended_items == [{"movie-001": "description"}]


def test_get_previous_recommend_items(
    slot_base_recommender: SlotBasedRecommenderModel,
) -> None:
    assert slot_base_recommender.get_previous_recommend_items() is None

    slot_base_recommender._db.backup_db_results = [{"movie-001": "description"}]
    assert slot_base_recommender.get_previous_recommend_items() == [
        {"movie-001": "description"}
    ]
