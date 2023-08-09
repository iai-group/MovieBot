from unittest.mock import MagicMock, Mock, patch

import pytest

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.values import Values
from moviebot.nlu.nlu import NLU
from tests.mocks.mock_data_loader import MockDataLoader


class MockChecker(MagicMock):
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
        "ontology": "",
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    nlu = NLU(config)
    nlu.intents_checker = MockChecker()
    return nlu


@pytest.fixture
def dialogue_state():
    dialogue_state = Mock()
    dialogue_state.item_in_focus = None
    dialogue_state.last_agent_dacts = []
    return dialogue_state


@pytest.mark.parametrize(
    "last_dact",
    [[], [DialogueAct(AgentIntents.ACKNOWLEDGE, [])]],
)
def test_no_intent(nlu, dialogue_state, last_dact):
    utterance = UserUtterance("random text that doesn't match any intent")
    dialogue_state.last_agent_dacts = last_dact
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


def test_selected_option(nlu, dialogue_state):
    utterance = UserUtterance("selected option")
    options = {DialogueAct(UserIntents.ACKNOWLEDGE, []): "selected option"}

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.ACKNOWLEDGE


def test_selected_option_continue_recommendation(nlu, dialogue_state):
    utterance = UserUtterance("selected option")
    options = {
        DialogueAct(UserIntents.CONTINUE_RECOMMENDATION, []): "selected option"
    }

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.CONTINUE_RECOMMENDATION


def test_reject_intent(nlu, dialogue_state):
    utterance = UserUtterance("reject text")
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.RECOMMEND, [])]
    dialogue_state.agent_made_offer = True

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.REJECT


def test_deny_intent(nlu, dialogue_state):
    utterance = UserUtterance("no")
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.WELCOME, [])]
    dialogue_state.agent_made_offer = True

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.INQUIRE


def test_reveal_voluntary_intent(nlu, dialogue_state):
    utterance = UserUtterance("voluntary reveal text")
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.WELCOME, [])]

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.REVEAL


def test_not_reveal_voluntary_intent(nlu, dialogue_state):
    utterance = UserUtterance("not reveal text")
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.WELCOME, [])]

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.UNK


def test_elicit_intent(nlu, dialogue_state):
    utterance = UserUtterance("reveal intent text")
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.ELICIT, [])]

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.REVEAL


def test_elicit_voluntary_intent(nlu, dialogue_state):
    utterance = UserUtterance("dont care text")
    options = {}

    dialogue_state.last_agent_dacts = [DialogueAct(AgentIntents.ELICIT, [])]

    dacts = nlu.generate_dacts(utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.REVEAL
