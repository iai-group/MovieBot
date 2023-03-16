import sqlite3

from moviebot.database.database import DataBase


class MockDataBase(DataBase):
    def __init__(self, path: str = None) -> None:
        self.sql_connection = sqlite3.connect(":memory:")
        self.db_table_name = "movies_test"
        self._insert_movies()
        self.current_CIN = None
        self.backup_db_results = None

    def _insert_movies(self) -> None:
        """Inserts sample of movies for tests."""
        cursor = self.sql_connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.db_table_name} (
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
            f"INSERT OR IGNORE INTO {self.db_table_name} VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "0114709",
                "Toy Story",
                "Animation, Adventure, Comedy, Family, Fantasy",
                "birthday party, action figure, moving, jealousy, birthday",
                8.3,
                851172,
                81,
                "Tom Hanks, Tim Allen, Don Rickles, Jim Varney, Wallace Shawn"
                "John Lasseter",
                "https://m.media-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@.jpg",  # noqa
                "A little boy named Andy loves to be in his room, playing with"
                'his toys, especially his doll named "Woody".',
                1995,
                "https://www.imdb.com/title/tt0114709/",
            ),
        )
        cursor.execute(
            f"INSERT OR IGNORE INTO {self.db_table_name} VALUES "
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
            f"INSERT OR IGNORE INTO {self.db_table_name} VALUES "
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
        self.sql_connection.commit()

    def test_method(self) -> int:
        return 123
