from unittest.mock import MagicMock, Mock, patch

import pytest

from moviebot.nlu.neural_nlu import NeuralNLU
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.core.core_types import DialogueOptions
from moviebot.dialogue_manager.dialogue_state import DialogueState
from tests.mocks.mock_data_loader import MockDataLoader

from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.core.intents.user_intents import UserIntents
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.values import Values


@pytest.fixture
def dialogue_state():
    dialogue_state = Mock()
    dialogue_state.item_in_focus = None
    dialogue_state.last_agent_dacts = []
    return dialogue_state

@pytest.fixture
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def nlu():
    config = {
        "domain": "",
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    nlu = NeuralNLU(config)
    return nlu 


@pytest.mark.parametrize(
    "last_dacts", [[], [DialogueAct(AgentIntents.ACKNOWLEDGE, [])]]
)
def test_generate_dacts(nlu,dialogue_state,last_dacts): 
    user_utterance = UserUtterance("I want to watch an action movie")
    dialogue_state.last_agent_dacts = last_dacts
    options = {}

    dacts = nlu.generate_dacts(user_utterance, options, dialogue_state)

    assert len(dacts) == 1
    assert dacts[0].intent == UserIntents.REVEAL
    
def test_annotate_utterance(nlu):
    user_utterance = UserUtterance("I want to watch an action movie") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 2
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I want"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "action"

    user_utterance = UserUtterance("Thank you for the recommendations,goodbye")
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "BYE"
    assert len(slots_info) == 0

    user_utterance = UserUtterance("Is this a comedy movie ?") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "INQUIRE"
    assert len(slots_info) == 1
    assert slots_info[0]["slot"] == "INQUIRE_GENRES"
    assert slots_info[0]["value"] == "comedy"

    
    user_utterance = UserUtterance("Recommend me a movie with Brad Pitt") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REMOVE_PREFERENCE"
    assert len(slots_info) == 1
    assert slots_info[0]["slot"] == "PREFERENCE_ACTORS"
    assert slots_info[0]["value"] == "Brad Pitt"


    user_utterance = UserUtterance("I like space movies") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 2
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I like"
    assert slots_info[1]["slot"] == "PREFERENCE_KEYWORDS"
    assert slots_info[1]["value"] == "space"

    user_utterance = UserUtterance("I hate horror movies") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 2
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I hate"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "horror"
    assert len(context_info) == 0


    user_utterance = UserUtterance("I love watching movies on a rainy night") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 1
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I love"
    assert len(context_info) == 1
    assert context_info[0]["context"] == "PREFERENCE_TIME"
    assert context_info[0]["value"] == "rainy night"
    
    user_utterance = UserUtterance("I love watching drama movies on a rainy night") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 2
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I love"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "drama"
    assert len(context_info) == 1
    assert context_info[0]["context"] == "PREFERENCE_TIME"
    assert context_info[0]["value"] == "rainy night"

    user_utterance = UserUtterance("I really enjoy watching drama movies on a rainy night") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 2
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I really enjoy"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "drama"
    assert len(context_info) == 1
    assert context_info[0]["context"] == "PREFERENCE_TIME"
    assert context_info[0]["value"] == "rainy night"

    user_utterance = UserUtterance("I'll be going on a date with my girlfriend this thursday evening and I need to find a good horror movie.") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "UNK"
    assert len(slots_info) == 1
    assert slots_info[0]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[0]["value"] == "horror"
    assert len(context_info) == 2
    assert context_info[0]["context"] == "PREFERENCE_COMPANION"
    assert context_info[0]["value"] == "girlfriend"
    assert context_info[1]["context"] == "PREFERENCE_TIME"
    assert context_info[1]["value"] == "thursday evening"

    user_utterance = UserUtterance("I hate christmas movies") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 2
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I hate"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "christmas"
    assert len(context_info) == 0

    user_utterance = UserUtterance("I hate watching movies at christmas") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "REVEAL"
    assert len(slots_info) == 1
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I hate"    
    assert len(context_info) == 1
    assert context_info[0]["context"] == "PREFERENCE_TIME"
    assert context_info[0]["value"] == "christmas"

    user_utterance = UserUtterance("I am looking for an action movie to watch with my siblings for the sunday afternoon.We love Brad Pitt. Can you recommend me something ?") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "UNK"
    assert len(slots_info) == 3
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I am"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "action"     
    assert slots_info[2]["slot"] == "PREFERENCE_ACTORS"
    assert slots_info[2]["value"] == "Brad Pitt"        
    assert len(context_info) == 2
    assert context_info[0]["context"] == "PREFERENCE_COMPANION"
    assert context_info[0]["value"] == "siblings"
    assert context_info[1]["context"] == "PREFERENCE_TIME"
    assert context_info[1]["value"] == "sunday afternoon"

    user_utterance = UserUtterance("I am looking for an action movie to watch with my siblings.We love Brad Pitt. Can you recommend me something ?") 
    intent, slots_info,context_info = nlu.annotate_utterance(user_utterance)
    assert intent == "UNK"
    assert len(slots_info) == 3
    assert slots_info[0]["slot"] == "PREFERENCE_MODIFIER"
    assert slots_info[0]["value"] == "I am looking"
    assert slots_info[1]["slot"] == "PREFERENCE_GENRES"
    assert slots_info[1]["value"] == "action"     
    assert slots_info[2]["slot"] == "PREFERENCE_ACTORS"
    assert slots_info[2]["value"] == "Brad Pitt"        
    assert len(context_info) == 1
    assert context_info[0]["context"] == "PREFERENCE_COMPANION"
    assert context_info[0]["value"] == "siblings"