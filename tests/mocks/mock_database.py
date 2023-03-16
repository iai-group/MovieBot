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
            f"INSERT OR IGNORE INTO {self.db_table_name} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "0114709",
                "Toy Story",
                "Animation, Adventure, Comedy, Family, Fantasy",
                "birthday party,  action figure,  moving,  jealousy,  birthday,  hat,  boy,  rivalry,  toy,  little boy,  cgi animation,  claw crane,  cowboy,  doll",
                8.3,
                851172,
                81,
                "Tom Hanks, Tim Allen, Don Rickles, Jim Varney, Wallace Shawn, John Ratzenberger",
                "John Lasseter",
                "https://m.media-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@.jpg",
                "A little boy named Andy loves to be in his room, playing with his toys, especially his doll named \"Woody\". But, what do the toys do when Andy is not with them, they come to life. Woody believes that his life (as a toy) is good. However, he must worry about Andy's family moving, and what Woody does not know is about Andy's birthday party. Woody does not realize that Andy's mother gave him an action figure known as Buzz Lightyear, who does not believe that he is a toy, and quickly becomes Andy's new favorite toy. Woody, who is now consumed with jealousy, tries to get rid of Buzz. Then, both Woody and Buzz are now lost. They must find a way to get back to Andy before he moves without them, but they will have to pass through a ruthless toy killer, Sid Phillips.",
                1995,
                "https://www.imdb.com/title/tt0114709/",
            ),
        )
        cursor.execute(
            f"INSERT OR IGNORE INTO {self.db_table_name} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "0113189",
                "GoldenEye",
                "Action, Adventure, Thriller",
                "electromagnetic pulse,  satellite,  weapon,  enemy,  fire,  chemical weapons,  assassin,  official james bond series,  007,  james bond character",
                7.2,
                231713,
                130,
                "Pierce Brosnan, Sean Bean, Izabella Scorupco, Famke Janssen, Joe Don Baker, Judi Dench",
                "Martin Campbell",
                "https://m.media-amazon.com/images/M/MV5BMzk2OTg4MTk1NF5BMl5BanBnXkFtZTcwNjExNTgzNA@@.jpg",
                'When a deadly satellite weapon system falls into the wrong hands, only Agent James Bond 007 (Pierce Brosnan) can save the world from certain disaster. Armed with his licence to kill, Bond races to Russia in search of the stolen access codes for "GoldenEye", an awesome space weapon that can fire a devastating electromagnetic pulse toward Earth. But 007 is up against an enemy who anticipates his every move: a mastermind motivated by years of simmering hatred. Bond also squares off against Xenia Onatopp (Famke Janssen), an assassin who uses pleasure as her ultimate weapon.',
                1995,
                "https://www.imdb.com/title/tt0113189/",
            ),
        )
        cursor.execute(
            f"INSERT OR IGNORE INTO {self.db_table_name} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "0114885",
                "Waiting to Exhale",
                "Comedy, Drama, Romance",
                "betrayal,  husband wife relationship,  mother son relationship,  f rated,  black american",
                5.9,
                9173,
                124,
                "Whitney Houston, Angela Bassett, Loretta Devine, Lela Rochon, Gregory Hines, Dennis Haysbert",
                "Forest Whitaker",
                "https://m.media-amazon.com/images/M/MV5BYzcyMDY2YWQtYWJhYy00OGQ2LTk4NzktYWJkNDYwZWJmY2RjXkEyXkFqcGdeQXVyMTA0MjU0Ng@@.jpg",
                "This story based on the best selling novel by Terry McMillan follows the lives of four African-American women as they try to deal with their very lives. Friendship becomes the strongest bond between these women as men, careers, and families take them in different directions. Often light-hearted this movie speaks about some of the problems and struggles the modern women face in today's world.",
                1995,
                "https://www.imdb.com/title/tt0114885/",
            ),
        )
        self.sql_connection.commit()

    def test_method(self) -> int:
        return 123
