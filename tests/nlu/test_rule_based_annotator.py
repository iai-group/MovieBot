"""Test rule based annotator (RBAnnotator)."""

import pytest

from moviebot.core.shared.utterance.utterance import UserUtterance
from moviebot.nlu.annotation.rule_based_annotator import RBAnnotator

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
