import sqlite3
from unittest.mock import patch

import pytest

from moviebot.database.database import DataBase
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.slots import Slots
from tests.mocks.mock_ontology import MockOntology


def _insert_movies(
    sql_connection: sqlite3.Connection, db_table_name: str
) -> None:
    """Inserts sample of movies for tests.

    Args:
        sql_connection: SQL connection.
        db_table_name: Name of the table to insert the movies.
    """
    cursor = sql_connection.cursor()
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {db_table_name} (
            ID TEXT,
            title TEXT,
            genres TEXT,
            keywords TEXT,
            imdb_rating float,
            imdb_votes INTEGER,
            duration INTEGER,
            actors TEXT,
            directors TEXT,
            cover_image TEXT,
            plot TEXT,
            year INTEGER,
            imdb_link TEXT)"""
    )

    # Insert 3 test movies
    cursor.execute(
        f"INSERT OR IGNORE INTO {db_table_name} VALUES "
        "(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "0114709",
            "Toy Story",
            "Animation, Adventure, Comedy, Family, Fantasy",
            "birthday party, action figure, moving, jealousy, birthday",
            8.3,
            851172,
            81,
            "Tom Hanks, Tim Allen, Don Rickles, Jim Varney, Wallace Shawn",
            "John Lasseter",
            "https://m.media-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@.jpg",  # noqa
            "A little boy named Andy loves to be in his room, playing with"
            'his toys, especially his doll named "Woody".',
            1995,
            "https://www.imdb.com/title/tt0114709/",
        ),
    )
    cursor.execute(
        f"INSERT OR IGNORE INTO {db_table_name} VALUES "
        "(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "0113189",
            "GoldenEye",
            "Action, Adventure, Thriller",
            "electromagnetic pulse, satellite, weapon, enemy, fire",
            7.2,
            231713,
            130,
            "Pierce Brosnan, Sean Bean, Izabella Scorupco, Famke Janssen",
            "Martin Campbell",
            "https://m.media-amazon.com/images/M/MV5BMzk2OTg4MTk1NF5BMl5BanBnXkFtZTcwNjExNTgzNA@@.jpg",  # noqa
            "When a deadly satellite weapon system falls into the wrong "
            "hands, only Agent James Bond 007 (Pierce Brosnan) can save the"
            " world from certain disaster.",
            1995,
            "https://www.imdb.com/title/tt0113189/",
        ),
    )
    cursor.execute(
        f"INSERT OR IGNORE INTO {db_table_name} VALUES "
        "(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "0114885",
            "Waiting to Exhale",
            "Comedy, Drama, Romance",
            "betrayal, husband wife relationship, mother son relationship",
            5.9,
            9173,
            124,
            "Whitney Houston, Angela Bassett, Loretta Devine, Lela Rochon",
            "Forest Whitaker",
            "https://m.media-amazon.com/images/M/MV5BYzcyMDY2YWQtYWJhYy00OGQ2LTk4NzktYWJkNDYwZWJmY2RjXkEyXkFqcGdeQXVyMTA0MjU0Ng@@.jpg",  # noqa
            "This story based on the best selling novel by Terry McMillan "
            "follows the lives of four African-American women as they try "
            "to deal with their very lives.",
            1995,
            "https://www.imdb.com/title/tt0114885/",
        ),
    )
    sql_connection.commit()


def init_mock(self, path: str) -> None:
    """Initializes mock database.

    Args:
        self: DataBase object.
        path: Path to the database file.
    """
    self.db_file_path = path
    self.sql_connection = sqlite3.connect(":memory:")
    self.db_table_name = "movies_test"
    self.current_CIN = None
    self.backup_db_results = None
    _insert_movies(self.sql_connection, self.db_table_name)


@pytest.fixture
@patch.object(DataBase, "__init__", lambda self, path: init_mock(self, path))
def database() -> DataBase:
    """Creates a mock database."""
    db = DataBase(None)
    assert db.db_file_path is None
    assert db.current_CIN is None
    return db


@pytest.fixture
@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def mock_dialogue_state() -> DialogueState:
    """Creates a mock representing agent_should_make_offer dialogue state."""
    dialogue_state = DialogueState(MockOntology(), [], isBot=False)
    dialogue_state.initialize()
    return dialogue_state


@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def test_get_sql_condition(
    database: DataBase, mock_dialogue_state: DialogueState
) -> None:
    # Empty current information need
    condition = database.get_sql_condition(mock_dialogue_state, MockOntology())
    assert condition is None

    # Non-empty current information need
    mock_dialogue_state.frame_CIN["year"] = "2023"
    mock_dialogue_state.frame_CIN["title"] = ".NOT.GoldenEye"
    condition = database.get_sql_condition(mock_dialogue_state, MockOntology())
    assert (
        condition
        == f'{Slots.YEAR} = 2023 AND {Slots.TITLE} NOT LIKE "%GoldenEye%"'
    )


@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def test_get_sql_condition_similar_movie(
    database: DataBase, mock_dialogue_state: DialogueState
) -> None:
    """Tests that the condition is correct when agent_should_offer_similar."""
    mock_dialogue_state.similar_movies = {
        "Toy Story": ["Toy Story 2", "Toy Story 3"],
        "Waiting to Exhale": ["Soul Food"],
    }
    mock_dialogue_state.agent_should_offer_similar = True
    condition = database.get_sql_condition(mock_dialogue_state, MockOntology())
    assert (
        condition
        == f'{Slots.TITLE} = "Toy Story 2" OR {Slots.TITLE} = "Toy Story 3"'
    )


@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def test_database_lookup(
    database: DataBase, mock_dialogue_state: DialogueState
) -> None:
    results = database.database_lookup(mock_dialogue_state, MockOntology())
    ids = set([movie.get("ID", None) for movie in results])
    assert len(ids) == 3
    assert ids == {"0114885", "0114709", "0113189"}


@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def test_database_lookup_empty_result(
    database: DataBase, mock_dialogue_state: DialogueState
) -> None:
    mock_dialogue_state.similar_movies = {"Toy Story": []}
    mock_dialogue_state.agent_should_offer_similar = True

    results = database.database_lookup(mock_dialogue_state, MockOntology())
    assert results == []


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
    slot: str, value: str, expected: str, database: DataBase
) -> None:
    output = database._get_value_for_query(slot, value)
    assert output == expected


def test__get_table_name(database: DataBase) -> None:
    assert database._get_table_name() == "movies_test"
