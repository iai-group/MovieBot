from typing import Any, Dict
from unittest import mock

import pytest

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_manager import DialogueManager
from moviebot.dialogue_manager.dialogue_policy.rb_dialogue_policy import (
    RuleBasedDialoguePolicy,
)
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.dialogue_manager.dialogue_state_tracker import (
    DialogueStateTracker,
)
from moviebot.domain.movie_domain import MovieDomain


@pytest.fixture
def config() -> Dict[str, Any]:
    with mock.patch(
        "moviebot.database.db_movies.DataBase"
    ) as MockDatabase, mock.patch(
        "moviebot.recommender.slot_based_recommender_model."
        "SlotBasedRecommenderModel"
    ) as MockRecommender:
        yield {
            "domain": MovieDomain("tests/data/test_domain.yaml"),
            "database": MockDatabase("tests/database/database.json"),
            "recommender": MockRecommender(
                MockDatabase("tests/database/database.json"),
                MovieDomain("tests/data/test_domain.yaml"),
            ),
        }


@pytest.fixture
def dialogue_manager(config) -> DialogueManager:
    yield DialogueManager(config, isBot=False, new_user=True)


def test_dialogue_manager(config):
    dialogue_manager = DialogueManager(config, isBot=False, new_user=True)
    assert hasattr(dialogue_manager, "dialogue_state_tracker")
    assert hasattr(dialogue_manager, "dialogue_policy")


@mock.patch.object(DialogueStateTracker, "initialize")
def test_start_dialogue(
    mocked_initialize: mock.MagicMock, dialogue_manager: DialogueManager
):
    agent_dact = dialogue_manager.start_dialogue()
    assert len(agent_dact) == 1
    assert agent_dact[0].intent == AgentIntents.WELCOME
    mocked_initialize.assert_called()


@mock.patch.object(DialogueStateTracker, "update_state_user")
def test_receive_input_empty(
    mocked_update_state_user: mock.MagicMock, dialogue_manager: DialogueManager
):
    dialogue_manager.receive_input([])
    mocked_update_state_user.assert_not_called()


@mock.patch.object(DialogueStateTracker, "update_state_user")
def test_receive_input(
    mocked_update_state_user: mock.MagicMock, dialogue_manager: DialogueManager
):
    dialogue_manager.receive_input(["asd"])
    mocked_update_state_user.assert_called()


def test_generate_output(dialogue_manager: DialogueManager):
    dialogue_manager.start_dialogue()
    dialogue_acts = dialogue_manager.generate_output()
    assert len(dialogue_acts) == 1
    assert dialogue_acts[0].intent == AgentIntents.WELCOME


@mock.patch.object(
    RuleBasedDialoguePolicy,
    "next_action",
    return_value=[DialogueAct(AgentIntents.ACKNOWLEDGE)],
)
@mock.patch.object(DialogueStateTracker, "update_state_agent")
def test_generate_output_next_action_called(
    mocked_update_state_agent: mock.MagicMock,
    mocked_next_action: mock.MagicMock,
    dialogue_manager: DialogueManager,
):
    dialogue_manager.start_dialogue()
    dialogue_acts = dialogue_manager.generate_output()
    mocked_next_action.assert_called()
    mocked_update_state_agent.assert_called()
    assert dialogue_acts == [DialogueAct(AgentIntents.ACKNOWLEDGE)]


@mock.patch.object(
    DialogueState,
    "agent_can_lookup",
    new_callable=mock.PropertyMock,
    return_value=True,
    create=True,
)
def test_generate_output_with_lookup(
    mock_agent_can_lookup, dialogue_manager: DialogueManager
):
    dialogue_manager.start_dialogue()
    dialogue_manager.generate_output()
    dialogue_manager.recommender.recommend_items.assert_called()


@mock.patch.object(
    RuleBasedDialoguePolicy,
    "next_action",
)
@mock.patch.object(DialogueStateTracker, "update_state_agent")
def test_generate_output_restart(
    mocked_update_state_agent: mock.MagicMock,
    mocked_next_action: mock.MagicMock,
    dialogue_manager: DialogueManager,
):
    dialogue_manager.start_dialogue()
    with mock.patch.object(
        DialogueStateTracker,
        "initialize",
        wraps=dialogue_manager.dialogue_state_tracker.initialize,
    ) as mocked_initialize:
        dialogue_manager.generate_output(restart=False)
        mocked_initialize.assert_not_called()
        dialogue_manager.generate_output(restart=True)
        mocked_initialize.assert_called()
        mocked_next_action.assert_called_with(mock.ANY, restart=True)
