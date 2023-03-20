import random
from unittest import mock

import pytest

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.dialogue_manager.dialogue_policy import DialoguePolicy
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.ontology.ontology import Ontology


@pytest.fixture
def ontology() -> Ontology:
    yield Ontology(path="tests/ontology/ontology.json")


@pytest.fixture
def state(ontology) -> DialogueState:
    dialogue_state = DialogueState(ontology, slots=[], isBot=False)
    dialogue_state.initialize()
    yield dialogue_state


@pytest.fixture
def policy(ontology) -> DialoguePolicy:
    yield DialoguePolicy(ontology, isBot=False, new_user=True)


def test_next_action(policy: DialoguePolicy, state: DialogueState):
    agent_dacts = policy.next_action(state)
    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == AgentIntents.WELCOME


def test_next_action_restart(policy: DialoguePolicy, state: DialogueState):
    agent_dacts = policy.next_action(state, restart=True)
    assert len(agent_dacts) == 2
    assert agent_dacts[0].intent == AgentIntents.RESTART
    assert agent_dacts[1].intent == AgentIntents.ELICIT


@mock.patch(
    "moviebot.dialogue_manager.dialogue_policy.set", mock.MagicMock(wraps=list)
)
def test__generate_examples(policy: DialoguePolicy):
    random.seed(42)
    examples = policy._generate_examples(
        [{"genre": "action, adventure"}, {"genre": "kung fu"}], "genre"
    )
    assert examples == "'adventure' or 'action'"
