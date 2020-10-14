from moviebot.nlu.annotators.slot_annotator import SlotAnnotator

from unittest.mock import patch
import pytest

slot_values = {
    'actors': {
        "Tom Hanson": "tom hanson",
        "Tom Hankason": "tom hankason",
        "Tom Hanslmaier": "tom hanslmaier",
        "Tom Handley": "tom handley",
    },
    'directors': {
        "Tom Hanks": "tom hank",
    },
}


@pytest.mark.parametrize('utterance, expected',
                         [('some other {} text'.format(name), name)
                          for name in slot_values['actors'].values()])
def test__person_name_annotator_actors(utterance, expected):
    # Setup
    annotator = SlotAnnotator(None, None, slot_values)

    # Exercise
    result = annotator._person_name_annotator(utterance)

    # Results
    assert len(result) == 1
    assert result[0].slot == 'actors'
    assert result[0].value == expected

    # Cleanup - none


def test__person_name_annotator_actor_and_director():
    # Setup
    slot_values = {
        'actors': {
            "Tom Hanks": "tom hank",
        },
        'directors': {
            "Tom Hanks": "tom hank",
        },
    }

    annotator = SlotAnnotator(None, None, slot_values)

    # Exercise
    utterance = 'some other text tom hank and after'
    result = annotator._person_name_annotator(utterance)

    # Results
    assert len(result) == 2
    slots = (r.slot for r in result)
    assert 'actors' in slots
    assert 'directors' in slots
    assert result[0].value == 'tom hank'

    # Cleanup - none


@pytest.mark.parametrize('utterance', [
    (''),
    ('i would like to watch an action movie'),
    ('im interested in something like othello'),
    ('im interested in something like hi cousin'),
])
def test__person_name_annotator_empty(utterance):
    # Setup
    annotator = SlotAnnotator(None, None, slot_values)

    # Exercise
    result = annotator._person_name_annotator(utterance)

    # Results
    assert result is None

    # Cleanup - none