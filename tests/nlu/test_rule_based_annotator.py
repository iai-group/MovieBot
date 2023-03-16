"""Test rule based annotator (RBAnnotator)."""

from typing import Dict
from unittest.mock import patch

import pytest

from moviebot.core.utterance.utterance import UserUtterance
from moviebot.nlu.annotation.rule_based_annotator import RBAnnotator
from moviebot.nlu.user_intents_checker import UserIntentsChecker
from tests.mocks.mock_data_loader import MockDataLoader
from tests.mocks.mock_ontology import MockOntology

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
    "genres": {
        "Action": "action",
        "Adventure": "adventure",
        "Crime": "crime",
    },
    "title": {
        "The Godfather": "the godfather",
        "The Godfather: Part II": "the godfather part ii",
        "Othello": "othello",
        "The Lion King": "the lion king",
    },
    "keywords": {
        "a birthday party": "a birthday party",
        "action figure": "action figure",
    },
}


def mock_process_value(text: str) -> str:
    """Returns a mock process value fixture."""
    return text


def mock_lematize_value(text: str) -> str:
    """Returns a mocked lematize value fixture."""
    return text


@pytest.fixture()
def annotator() -> RBAnnotator:
    """Returns a rule based annotator fixture."""
    return RBAnnotator(mock_process_value, mock_lematize_value, SLOT_VALUES)


@pytest.fixture()
@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def uic() -> UserIntentsChecker:
    """Returns a user intent checker fixture with an ontology."""
    config = {
        "ontology": MockOntology(),
        "database": "",
        "slot_values_path": "",
        "tag_words_slots_path": "",
    }
    uic = UserIntentsChecker(config)
    return uic


@pytest.mark.parametrize(
    "slot, message",
    [
        ("year", {"text": "a good movie"}),
        ("plot", {"text": "Some movie with a plot"}),
    ],
)
def test_slot_annotation_empty(
    annotator: RBAnnotator, slot: str, message: Dict[str, str]
) -> None:
    result = annotator.slot_annotation(slot, UserUtterance(message))

    assert len(result) == 0


@pytest.mark.parametrize(
    "slot, message, operator, value",
    [
        ("year", {"text": "a new movie"}, "=", "> 2010"),
        (
            "actors",
            {"text": "a movie starring tom handley"},
            "=",
            "tom handley",
        ),
        (
            "genres",
            {"text": "a movie with action."},
            "=",
            "action",
        ),
    ],
)
def test_slot_annotation(
    annotator: RBAnnotator,
    slot: str,
    message: Dict[str, str],
    operator: str,
    value: str,
) -> None:
    result = annotator.slot_annotation(slot, UserUtterance(message))

    assert len(result) == 1
    assert result[0].value == value
    assert str(result[0].op) == operator


def test__genres_annotator_empty(annotator: RBAnnotator) -> None:
    result = annotator._genres_annotator(
        "genres", UserUtterance({"text": "a movie"})
    )

    assert len(result) == 0


@pytest.mark.parametrize(
    "message, operator, value",
    [
        ({"text": "a crime movie"}, "=", "crime"),
        (
            {"text": "a movie with action and adventure"},
            "=",
            "action adventure",
        ),
        ({"text": "a dramatical movie"}, "=", "dramatical"),
        ({"text": "a crime movie, but animated"}, "=", "crime animated"),
    ],
)
def test__genres_annotator(
    annotator: RBAnnotator, message: Dict[str, str], operator: str, value: str
) -> None:
    result = annotator._genres_annotator("genres", UserUtterance(message))

    assert len(result) == 1
    assert result[0].value == value
    assert str(result[0].op) == operator


def test__title_annotator_empty(annotator: RBAnnotator) -> None:
    result = annotator._title_annotator(
        "title", UserUtterance({"text": "a weekend trip movie"})
    )

    assert len(result) == 0


@pytest.mark.parametrize(
    "message, operator, value",
    [
        ({"text": "One of the godfather movies"}, "=", "the godfather"),
        ({"text": "How about Othello"}, "=", "othello"),
        ({"text": "Movie about a lion king"}, "=", "lion king"),
    ],
)
def test__title_annotator(
    annotator: RBAnnotator, message: Dict[str, str], operator: str, value: str
) -> None:
    result = annotator._title_annotator("title", UserUtterance(message))

    assert len(result) == 1
    assert result[0].value == value
    assert str(result[0].op) == operator


def test__keywords_annotator_empty(annotator: RBAnnotator) -> None:
    result = annotator._keywords_annotator(
        "keywords", UserUtterance({"text": "a weekend trip movie"})
    )

    assert len(result) == 0


@pytest.mark.parametrize(
    "message, operator, value",
    [
        ({"text": "Something with action figures"}, "=", "action figure"),
        (
            {"text": "I like movies with birthday party"},
            "=",
            "birthday party",
        ),
    ],
)
def test__keywords_annotator(
    annotator: RBAnnotator, message: Dict[str, str], operator: str, value: str
) -> None:
    result = annotator._keywords_annotator("keywords", UserUtterance(message))

    assert len(result) == 1
    assert result[0].value == value
    assert str(result[0].op) == operator


@pytest.mark.parametrize(
    "utterance, expected",
    [
        (UserUtterance({"text": f"some other {name} text"}), name)
        for name in SLOT_VALUES["actors"].values()
    ],
)
def test__person_name_annotator_actors(
    annotator: RBAnnotator, utterance: UserUtterance, expected: str
) -> None:
    result = annotator._person_name_annotator(utterance)

    assert len(result) == 1
    assert result[0].slot == "actors"
    assert result[0].value == expected


def test__person_name_annotator_actor_and_director(
    annotator: RBAnnotator,
) -> None:
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
def test__person_name_annotator_empty(
    annotator: RBAnnotator, utterance: UserUtterance
) -> None:
    result = annotator._person_name_annotator(utterance)
    assert len(result) == 0


@pytest.mark.parametrize(
    "message, operator, value",
    [
        ({"text": "i would like to watch a movie from 1999"}, "=", "1999"),
        ({"text": "i would like to watch a movie from 1999s"}, "=", "1999"),
        ({"text": "i would like to watch a new movie"}, ">", "2010"),
        ({"text": "i would like to watch a old movie"}, "<", "2010"),
        ({"text": "Give me a movie from 1970s"}, "BETWEEN", "1970 AND 1980"),
        ({"text": "Anything from the 50s?"}, "BETWEEN", "1950 AND 1960"),
        ({"text": "A movie from 20th century"}, "BETWEEN", "1900 AND 2000"),
        ({"text": "A movie from 21st century"}, "BETWEEN", "2000 AND 2100"),
    ],
)
def test__year_annotator(
    annotator: RBAnnotator, message: Dict[str, str], operator: str, value: str
) -> None:
    utterance = UserUtterance(message)
    result = annotator._year_annotator("year", utterance)

    assert len(result) == 1
    assert result[0].value == value
    assert str(result[0].op) == operator


@pytest.mark.parametrize(
    "raw_utterance, gram, ngram_size, expected",
    [
        ("i would like to watch something funny+romantic", "funny", 1, "funny"),
        ("im interested in something about kung-fu", "kung fu", 2, "kung fu"),
    ],
)
def test_find_in_raw_utterance(
    uic: UserIntentsChecker,
    raw_utterance: str,
    gram: str,
    ngram_size: int,
    expected: str,
):
    annotator = RBAnnotator(
        uic._process_utterance, uic._lemmatize_value, SLOT_VALUES
    )
    result = annotator.find_in_raw_utterance(raw_utterance, gram, ngram_size)

    assert result == expected
