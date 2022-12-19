"""Test rule based annotator (RBAnnotator)."""

from unittest.mock import patch

import pytest
from tests.mocks.mock_data_loader import MockDataLoader
from tests.mocks.mock_ontology import MockOntology

from moviebot.core.utterance.utterance import UserUtterance
from moviebot.nlu.annotation.rule_based_annotator import RBAnnotator
from moviebot.nlu.user_intents_checker import UserIntentsChecker

SLOT_VALUES = {
    "actors": {
        "Tom Hanson": "tom hanson",
        "Tom Hankason": "tom hankason",
        "Tom Hanslmaier": "tom hanslmaier",
        "Tom Handley": "tom handley",
    },
    "directors": {
        "Tom Hanks": "tom hank",
    },
}

@pytest.fixture()
@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def uic() -> UserIntentsChecker:
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
    "utterance, expected",
    [
        (UserUtterance({"text": "some other {} text".format(name)}), name)
        for name in SLOT_VALUES["actors"].values()
    ],
)
def test__person_name_annotator_actors(
    utterance: UserUtterance, expected: str
) -> None:
    annotator = RBAnnotator(None, None, SLOT_VALUES)
    result = annotator._person_name_annotator(utterance)

    assert len(result) == 1
    assert result[0].slot == "actors"
    assert result[0].value == expected


def test__person_name_annotator_actor_and_director() -> None:
    annotator = RBAnnotator(None, None, SLOT_VALUES)

    utterance = UserUtterance(
        {"text": "some other text tom hank and after tom handley"}
    )
    result = annotator._person_name_annotator(utterance)

    assert len(result) == 2
    slots = [r.slot for r in result]
    assert "actors" in slots
    assert "directors" in slots
    assert result[0].value == "tom hank"


@pytest.mark.parametrize(
    "utterance",
    [
        (UserUtterance({"text": ""})),
        (UserUtterance({"text": "i would like to watch an action movie"})),
        (UserUtterance({"text": "im interested in something like othello"})),
        (UserUtterance({"text": "im interested in something like hi cousin"})),
    ],
)
def test__person_name_annotator_empty(utterance: UserUtterance) -> None:
    annotator = RBAnnotator(None, None, SLOT_VALUES)
    result = annotator._person_name_annotator(utterance)
    assert result is None


@pytest.mark.parametrize(
    "raw_utterance, gram, ngram_size, expected",
    [
        ("i would like to watch something funny+romantic", "funny", 1, "funny"),
        ("im interested in something about kung-fu", "kung fu", 2, "kung fu"),
    ],
)
def test_find_in_raw_utterance(uic: UserIntentsChecker, raw_utterance: str, gram: str, ngram_size: int, expected: str):
    annotator = RBAnnotator(uic._process_utterance, uic._lemmatize_value, SLOT_VALUES)
    result = annotator.find_in_raw_utterance(raw_utterance, gram, ngram_size)

    assert result == expected
