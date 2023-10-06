from unittest.mock import MagicMock, Mock, patch

import pytest

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.values import Values
from moviebot.nlu.rule_based_nlu import RuleBasedNLU
from tests.mocks.mock_data_loader import MockDataLoader


class MockIntentChecker(MagicMock):
    def check_basic_intent(self, user_utterance, intent):
        if intent == UserIntents.BYE and user_utterance.text == "bye":
            return [DialogueAct(UserIntents.BYE, [])]
        if intent == UserIntents.DENY and user_utterance.text == "no":
            return [DialogueAct(UserIntents.DENY, [])]
        return []

    def check_reveal_voluntary_intent(self, user_utterance):
        if user_utterance.text == "voluntary reveal text":
            return [DialogueAct(UserIntents.REVEAL, [])]
        return []

    def check_reveal_intent(self, user_utterance, last_agent_dact):
        if last_agent_dact.intent == AgentIntents.ELICIT:
            if user_utterance.text == "reveal intent text":
                return [DialogueAct(UserIntents.REVEAL, [])]
            elif user_utterance.text == "dont care text":
                constraint = ItemConstraint("", Operator.EQ, Values.DONT_CARE)
                return [
                    DialogueAct(
                        UserIntents.REVEAL,
                        [constraint],
                    )
                ]
        return []

    def check_reject_intent(self, user_utterance):
        if user_utterance.text == "reject text":
            return [DialogueAct(UserIntents.REJECT, [])]
        return []

    def check_inquire_intent(self, user_utterance):
        if user_utterance.text == "inquire text":
            return [DialogueAct(UserIntents.INQUIRE, [])]
        return []


@pytest.fixture
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def nlu():
    config = {
        "domain": "",
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    nlu = RuleBasedNLU(config)
    nlu.intents_checker = MockIntentChecker()
    return nlu


@pytest.fixture
def dialogue_state():
    dialogue_state = Mock()
    dialogue_state.item_in_focus = None
    dialogue_state.last_agent_dacts = []
    return dialogue_state


@pytest.mark.parametrize(
    "last_dacts", [[], [DialogueAct(AgentIntents.ACKNOWLEDGE, [])]]
)
def test_no_intent(nlu, dialogue_state, last_dacts):
    utterance = UserUtterance("random text that doesn't match any intent")
    dialogue_state.last_agent_dacts = last_dacts
    options = {}

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.UNK


def test_basic_bye_intent(nlu, dialogue_state):
    utterance = UserUtterance("bye")
    options = {}

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.BYE


@pytest.mark.parametrize(
    "user_intent",
    [UserIntents.ACKNOWLEDGE, UserIntents.CONTINUE_RECOMMENDATION],
)
def test_selected_option(nlu, dialogue_state, user_intent):
    utterance = UserUtterance("selected option")
    options = {DialogueAct(user_intent): "selected option"}

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == user_intent


@pytest.mark.parametrize(
    "last_dacts, utterance, expected_intent",
    [
        (
            [DialogueAct(AgentIntents.WELCOME, [])],
            "reject text",
            UserIntents.REJECT,
        ),
        ([DialogueAct(AgentIntents.RECOMMEND, [])], "no", UserIntents.INQUIRE),
    ],
)
def test_deny_intent(
    nlu, dialogue_state, last_dacts, utterance, expected_intent
):
    utterance = UserUtterance(utterance)
    options = {}

    dialogue_state.last_agent_dacts = last_dacts
    dialogue_state.agent_made_offer = True

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == expected_intent


@pytest.mark.parametrize(
    "utterance, expected_intent",
    [
        ("voluntary reveal text", UserIntents.REVEAL),
        ("not reveal text", UserIntents.UNK),
    ],
)
def test_reveal_voluntary_intent(
    nlu, dialogue_state, utterance, expected_intent
):
    utterance = UserUtterance(utterance)
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.WELCOME, [])]

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == expected_intent


@pytest.mark.parametrize("utterance", ["reveal intent text", "dont care text"])
def test_elicit_intent(nlu, dialogue_state, utterance):
    utterance = UserUtterance(utterance)
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.ELICIT, [])]

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.REVEAL
