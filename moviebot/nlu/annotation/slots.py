"""This file contains the list of slots available in the database.
This approach will help the NLU to correctly identify slots"""


from enum import Enum


class Slots(Enum):
    """This class contains the list of slots available in the database. This
    approach will help the NLU to correctly identify slots"""

    ID = "ID"
    TITLE = "title"
    GENRES = "genres"
    KEYWORDS = "keywords"
    DIRECTORS = "directors"
    DURATION = "duration"
    ACTORS = "actors"
    PLOT = "plot"
    YEAR = "year"
    MOVIE_LINK = "imdb_link"
    COVER_IMAGE = "cover_image"
    RATING = "imdb_rating"
    MORE_INFO = "more_info"

    def __str__(self):
        return str(self.value)
