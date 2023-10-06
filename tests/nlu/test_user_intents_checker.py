"""Tests for UserIntentsChecker class."""
from unittest.mock import patch

import pytest

from moviebot.core.intents.user_intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.domain.movie_domain import MovieDomain
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


@pytest.fixture()
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def uic1() -> UserIntentsChecker:
    """Returns a user intent checker fixture."""
    config = {
        "domain": "",
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    uic = UserIntentsChecker(config)
    return uic


@pytest.fixture()
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def uic2() -> UserIntentsChecker:
    """Returns a user intent checker fixture with a domain."""
    config = {
        "domain": MovieDomain("tests/data/test_domain.yaml"),
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    uic = UserIntentsChecker(config)
    return uic


@pytest.mark.parametrize(
    "utterance, intent",
    [
        (UserUtterance("hello"), UserIntents.HI),
        (
            UserUtterance("hi do you know of any interesting movies"),
            UserIntents.HI,
        ),
        (UserUtterance("hey hey"), UserIntents.HI),
        (UserUtterance("exit"), UserIntents.BYE),
        (
            UserUtterance("im happy with my result bye"),
            UserIntents.BYE,
        ),
        (UserUtterance("yes"), UserIntents.ACKNOWLEDGE),
        (
            UserUtterance("That's fine thank you"),
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
            UserUtterance("i would like to watch an action movie"),
            UserIntents.HI,
        ),
        (
            UserUtterance("hi do you know of any interesting movies"),
            UserIntents.BYE,
        ),
        (
            UserUtterance("No I do not like it"),
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
            UserUtterance("Recommend me a movie with tom hank"),
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
            UserUtterance("Recommend me a movie directed by howard deutch"),
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
        (UserUtterance("i would like to watch an action movie")),
        (UserUtterance("bye")),
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
            UserUtterance("i would like another movie"),
            DialogueAct(
                UserIntents.REJECT,
                [
                    ItemConstraint(
                        "reason",
                        Operator.EQ,
                        "dont_like",
                    ),
                    ItemConstraint(
                        "preference",
                        Operator.EQ,
                        -1.0,
                    ),
                ],
            ),
        ),
        (
            UserUtterance("I have already seen this movie"),
            DialogueAct(
                UserIntents.REJECT,
                [
                    ItemConstraint(
                        "reason",
                        Operator.EQ,
                        "watched",
                    ),
                    ItemConstraint(
                        "preference",
                        Operator.EQ,
                        0.0,
                    ),
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
