"""Tests for UserIntentsChecker class."""
from unittest.mock import patch

import pytest

from moviebot.core.shared.intents.user_intents import UserIntents
from moviebot.core.shared.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.semantic_annotation import (
    AnnotationType,
    EntityType,
    SemanticAnnotation,
)
from moviebot.nlu.text_processing import Span
from moviebot.nlu.user_intents_checker import UserIntentsChecker
from tests.mocks.mock_data_loader import MockDataLoader
from tests.mocks.mock_ontology import MockOntology


@pytest.fixture()
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def uic1() -> UserIntentsChecker:
    """Returns a user intent checker fixture."""
    config = {
        "ontology": "",
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    uic = UserIntentsChecker(config)
    return uic


@pytest.fixture()
@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def uic2() -> UserIntentsChecker:
    """Returns a user intent checker fixture with an ontology."""
    config = {
        "ontology": MockOntology(None).load_ontolgy(),
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    uic = UserIntentsChecker(config)
    return uic


@pytest.mark.parametrize(
    "utterance, intent",
    [
        (UserUtterance({"text": "hello"}), UserIntents.HI),
        (
            UserUtterance({"text": "hi do you know of any interesting movies"}),
            UserIntents.HI,
        ),
        (UserUtterance({"text": "hey hey"}), UserIntents.HI),
        (UserUtterance({"text": "exit"}), UserIntents.BYE),
        (
            UserUtterance({"text": "im happy with my result bye"}),
            UserIntents.BYE,
        ),
        (UserUtterance({"text": "yes"}), UserIntents.ACKNOWLEDGE),
        (
            UserUtterance({"text": "That's fine thank you"}),
            UserIntents.ACKNOWLEDGE,
        ),
    ],
)
def test_check_basic_intent(
    uic1: UserIntentsChecker, utterance: UserUtterance, intent: UserIntents
) -> None:
    result = uic1.check_basic_intent(utterance, intent)

    assert len(result) == 1
    assert result[0].intent == intent


@pytest.mark.parametrize(
    "utterance, intent",
    [
        (
            UserUtterance({"text": "i would like to watch an action movie"}),
            UserIntents.HI,
        ),
        (
            UserUtterance({"text": "hi do you know of any interesting movies"}),
            UserIntents.BYE,
        ),
        (
            UserUtterance({"text": "No I do not like it"}),
            UserIntents.ACKNOWLEDGE,
        ),
    ],
)
def test_check_basic_intent_empty(
    uic1: UserIntentsChecker, utterance: UserUtterance, intent: UserIntents
) -> None:
    result = uic1.check_basic_intent(utterance, intent)
    assert len(result) == 0


@pytest.mark.parametrize(
    "utterance, is_question",
    [
        ("i would like to watch an action movie", False),
        ("when was inception released", True),
        ("Who was the lead actor?", True),
    ],
)
def test__is_question(
    uic1: UserIntentsChecker, utterance: str, is_question: bool
) -> None:
    result = uic1._is_question(utterance)
    assert result == is_question


@pytest.mark.parametrize(
    "utterance, dact",
    [
        (
            UserUtterance({"text": "Recommend me a movie with tom hank"}),
            DialogueAct(
                UserIntents.REVEAL,
                [
                    ItemConstraint(
                        "actors",
                        Operator.EQ,
                        "tom hank",
                        SemanticAnnotation.from_span(
                            Span("tom hank", 26, 34, "tom hank"),
                            AnnotationType.NAMED_ENTITY,
                            EntityType.PERSON,
                        ),
                    )
                ],
            ),
        ),
        (
            UserUtterance(
                {"text": "Recommend me a movie directed by howard deutch"}
            ),
            DialogueAct(
                UserIntents.REVEAL,
                [
                    ItemConstraint(
                        "directors",
                        Operator.EQ,
                        "howard deutch",
                        SemanticAnnotation.from_span(
                            Span("howard deutch", 33, 46, "howard deutch"),
                            AnnotationType.NAMED_ENTITY,
                            EntityType.PERSON,
                        ),
                    )
                ],
            ),
        ),
    ],
)
def test_check_reveal_voluntary_intent(
    uic2: UserIntentsChecker, utterance: UserUtterance, dact: DialogueAct
) -> None:
    result = uic2.check_reveal_voluntary_intent(utterance)

    assert result[0].intent == dact.intent
    assert result[0].params == dact.params


@pytest.mark.parametrize(
    "utterance",
    [
        (UserUtterance({"text": "i would like to watch an action movie"})),
        (UserUtterance({"text": "bye"})),
    ],
)
def test_check_reveal_voluntary_intent_empty(
    uic2: UserIntentsChecker, utterance: UserUtterance
) -> None:
    result = uic2.check_reveal_voluntary_intent(utterance)
    assert len(result) == 0


@pytest.mark.parametrize(
    "utterance, dact",
    [
        (
            UserUtterance({"text": "i would like another movie"}),
            DialogueAct(
                UserIntents.REJECT,
                [
                    ItemConstraint(
                        "reason",
                        Operator.EQ,
                        "dont_like",
                    )
                ],
            ),
        ),
        (
            UserUtterance({"text": "I have already seen this movie"}),
            DialogueAct(
                UserIntents.REJECT,
                [
                    ItemConstraint(
                        "reason",
                        Operator.EQ,
                        "watched",
                    )
                ],
            ),
        ),
    ],
)
def test_check_reject_intent(
    uic1: UserIntentsChecker, utterance: UserUtterance, dact: DialogueAct
) -> None:
    result = uic1.check_reject_intent(utterance)

    assert result[0].intent == dact.intent
    assert result[0].params == dact.params
