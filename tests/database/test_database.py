"""Tests for DataBase."""
from unittest.mock import patch

import pytest

import moviebot.database.database as DB
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.slots import Slots
from tests.mocks.mock_data_loader import MockDataLoader
from tests.mocks.mock_database import MockDataBase
from tests.mocks.mock_ontology import MockOntology


@patch("moviebot.database.database.DataBase", new=MockDataBase)
def test_mock_database() -> None:
    db = DB.DataBase(None)
    result = db.test_method()
    truth = 123
    assert result == truth


@pytest.fixture()
@patch("moviebot.database.database.DataBase", new=MockDataBase)
def database() -> MockDataBase:
    db = MockDataBase()
    assert db._get_table_name() == "movies_test"
    return db


@pytest.fixture()
@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def ontology() -> MockOntology:
    return MockOntology()


@pytest.fixture()
@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
@patch("moviebot.nlu.user_intents_checker.DataLoader", new=MockDataLoader)
def dialogue_state() -> DialogueState:
    slots = list(MockDataLoader(None, None).load_slot_value_pairs().keys())
    ds = DialogueState(MockOntology(), slots, False)
    ds.initialize()
    return ds


def test_get_sql_condition(
    database: MockDataBase,
    ontology: MockOntology,
    dialogue_state: DialogueState,
) -> None:
    condition = database.get_sql_condition(dialogue_state, ontology)
    assert condition is None

    dialogue_state.frame_CIN["year"] = "2023"
    dialogue_state.frame_CIN["title"] = ".NOT.GoldenEye"
    condition = database.get_sql_condition(dialogue_state, ontology)
    assert (
        condition
        == f'{Slots.YEAR} = 2023 AND {Slots.TITLE} NOT LIKE "%GoldenEye%"'
    )


def test_database_lookup(
    database: MockDataBase,
    ontology: MockOntology,
    dialogue_state: DialogueState,
) -> None:
    results = database.database_lookup(dialogue_state, ontology)
    ids = set([movie.get("ID", None) for movie in results])
    assert len(ids) == 3
    assert ids == {"0114885", "0114709", "0113189"}


@pytest.mark.parametrize(
    "slot, value, expected",
    [
        ("title", "GoldenEye", 'LIKE "%GoldenEye%"'),
        ("title", ".NOT.GoldenEye", 'NOT LIKE "%GoldenEye%"'),
        ("year", "2023", "= 2023"),
        ("year", ".NOT.2023", "NOT 2023"),
        ("year", ".NOT.>2023", "<2023"),
        ("year", ".NOT.<2023", ">2023"),
    ],
)
def test___get_value_for_query(
    slot: str, value: str, expected: str, database: MockDataBase
) -> None:
    output = database._get_value_for_query(slot, value)
    assert output == expected
