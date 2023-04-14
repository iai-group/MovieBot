import pytest

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator


@pytest.mark.parametrize(
    "intent",
    [
        None,
        ("wrong_intent",),
    ],
)
def test_dialogue_act_wrong_intent(intent):
    with pytest.raises(ValueError):
        DialogueAct(intent)


def test_dialogue_act_with_intent():
    da = DialogueAct(AgentIntents.BYE)
    assert da.intent == AgentIntents.BYE
    assert da.params == []


def test_dialogue_act_with_intent_and_params():
    params = [
        ItemConstraint("param1", Operator.EQ, ""),
        ItemConstraint("param2", Operator.EQ, ""),
    ]
    da = DialogueAct(UserIntents.ACKNOWLEDGE, params)
    assert da.intent == UserIntents.ACKNOWLEDGE
    assert da.params == params


def test_dialogue_act_wrong_params_format():
    with pytest.raises(AssertionError):
        DialogueAct(UserIntents.CONTINUE_RECOMMENDATION, ["wrong_params"])


def test_dialogue_act_remove_constraint():
    param1 = ItemConstraint("param1", Operator.AND, "")
    param2 = ItemConstraint("param2", Operator.GE, "")
    da = DialogueAct(UserIntents.REMOVE_PREFERENCE, [param1, param2])
    da.remove_constraint(ItemConstraint("param1", Operator.AND, ""))
    assert da.params == [param2]
