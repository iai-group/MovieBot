import random
from unittest import mock

import pytest

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_policy.rb_dialogue_policy import (
    RuleBasedDialoguePolicy,
)
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator


@pytest.fixture
def slots():
    return list(str(x) for x in range(5))


@pytest.fixture
def database_results():
    return [
        {"title": "The Matrix", "year": 1999, "genre": "action"},
        {"title": "The Matrix Reloaded", "year": 2003, "genre": "action"},
        {"title": "The Matrix Revolutions", "year": 2003, "genre": "action"},
    ]


@pytest.fixture
def domain() -> MovieDomain:
    yield MovieDomain("tests/data/test_domain.yaml")


@pytest.fixture
def state(domain, database_results, slots) -> DialogueState:
    dialogue_state = DialogueState(domain, slots=slots, isBot=False)
    dialogue_state.initialize()
    dialogue_state.agent_requestable = slots
    dialogue_state.database_result = database_results
    yield dialogue_state


@pytest.fixture
def policy() -> RuleBasedDialoguePolicy:
    yield RuleBasedDialoguePolicy(isBot=False, new_user=True)


@pytest.mark.parametrize(
    "last_user_dacts, last_agent_dacts, expected",
    [
        ([], [], AgentIntents.WELCOME),
        (
            [DialogueAct(UserIntents.HI)],
            [DialogueAct(AgentIntents.WELCOME)],
            AgentIntents.ELICIT,
        ),
        (
            [DialogueAct(UserIntents.UNK)],
            [DialogueAct(AgentIntents.WELCOME)],
            AgentIntents.ELICIT,
        ),
        ([DialogueAct(UserIntents.BYE)], [], AgentIntents.BYE),
        (
            [DialogueAct(UserIntents.UNK)],
            [],
            AgentIntents.ELICIT,
        ),
    ],
)
def test_next_action_basic(
    policy: RuleBasedDialoguePolicy,
    state: DialogueState,
    last_agent_dacts,
    last_user_dacts,
    expected,
):
    state.last_user_dacts = last_user_dacts
    state.last_agent_dacts = last_agent_dacts
    agent_dacts = policy.next_action(state)
    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == expected


def test_next_action_restart(
    policy: RuleBasedDialoguePolicy, state: DialogueState
):
    agent_dacts = policy.next_action(state, restart=True)
    assert len(agent_dacts) == 2
    assert agent_dacts[0].intent == AgentIntents.RESTART
    assert agent_dacts[1].intent == AgentIntents.ELICIT


def test_next_action_made_partial_offer(
    policy: RuleBasedDialoguePolicy, state: DialogueState
):
    state.agent_made_partial_offer = True

    state.last_user_dacts = [DialogueAct(UserIntents.UNK)]
    state.last_agent_dacts = []

    agent_dacts = policy.next_action(state)

    assert len(agent_dacts) == 2
    assert agent_dacts[0].intent == AgentIntents.COUNT_RESULTS
    assert agent_dacts[1].intent == AgentIntents.ELICIT


def test_next_action_made_partial_offer_all_slots_filled(
    policy: RuleBasedDialoguePolicy, state: DialogueState
):
    state.agent_made_partial_offer = True
    state.slot_left_unasked = 10
    state.last_user_dacts = [DialogueAct(UserIntents.UNK)]
    state.last_agent_dacts = []

    agent_dacts = policy.next_action(state)

    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == AgentIntents.RECOMMEND


def test_next_action_should_make_offer(
    policy: RuleBasedDialoguePolicy, state: DialogueState, database_results
):
    state.agent_should_make_offer = True
    state.item_in_focus = database_results[1]
    state.last_user_dacts = [DialogueAct(UserIntents.REVEAL)]

    agent_dacts = policy.next_action(state)

    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == AgentIntents.RECOMMEND
    assert len(agent_dacts[0].params) == 1
    assert agent_dacts[0].params[0].value == "The Matrix Reloaded"


def test_next_action_inquire_empty(
    policy: RuleBasedDialoguePolicy, state: DialogueState, database_results
):
    state.agent_made_offer = True
    state.item_in_focus = database_results[2]
    state.last_user_dacts = [DialogueAct(UserIntents.INQUIRE, [])]

    agent_dacts = policy.next_action(state)

    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == AgentIntents.INFORM
    assert len(agent_dacts[0].params) == 1
    assert agent_dacts[0].params[0].slot == "deny"
    assert agent_dacts[0].params[0].value == "The Matrix Revolutions"


def test_next_action_inquire(
    policy: RuleBasedDialoguePolicy, state: DialogueState, database_results
):
    state.agent_made_offer = True
    state.item_in_focus = database_results[2]
    state.last_user_dacts = [
        DialogueAct(
            UserIntents.INQUIRE, [ItemConstraint("genre", Operator.EQ, "")]
        )
    ]

    agent_dacts = policy.next_action(state)

    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == AgentIntents.INFORM
    assert len(agent_dacts[0].params) == 1
    assert agent_dacts[0].params[0].slot == "genre"
    assert agent_dacts[0].params[0].value == "action"


def test_next_action_accept_recommendation(
    policy: RuleBasedDialoguePolicy, state: DialogueState, database_results
):
    state.agent_made_offer = True
    state.item_in_focus = database_results[1]
    state.last_user_dacts = [DialogueAct(UserIntents.ACCEPT, [])]

    agent_dacts = policy.next_action(state)

    assert len(agent_dacts) == 1
    assert agent_dacts[0].intent == AgentIntents.CONTINUE_RECOMMENDATION
    assert len(agent_dacts[0].params) == 1
    assert agent_dacts[0].params[0].slot == "title"
    assert agent_dacts[0].params[0].value == "The Matrix Reloaded"


@pytest.mark.parametrize(
    "results, slot, expected",
    [
        (
            [{"keyword": "war"}],
            "keyword",
            "'war'",
        ),
        (
            [{"genre": "action, adventure"}, {"genre": "kung fu"}],
            "genre",
            "'kung fu' or 'action'",
        ),
        (
            [{"actor": "bruce lee," * 100}],
            "actor",
            "'bruce lee' or 'bruce lee'",
        ),
    ],
)
@mock.patch(
    "moviebot.dialogue_manager.dialogue_policy.rb_dialogue_policy.set",
    mock.MagicMock(wraps=list),
)
def test__generate_examples(
    policy: RuleBasedDialoguePolicy, results, slot, expected
):
    random.seed(42)
    examples = policy._generate_examples(results, slot)
    assert examples == expected
