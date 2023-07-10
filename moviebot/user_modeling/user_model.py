"""Class for user modeling."""


from collections import defaultdict
from typing import Dict, List

from moviebot.database.database import DataBase


class UserModel:
    def __init__(self, user_id: str, movie_choices: Dict[str, str] = None):
        """Initializes the user model.

        Args:
            user_id: User id.
            movie_choices: Dictionary with movie choices (i.e., accept, reject).
              Defaults to None.
        """
        self.user_id = user_id
        self._movies_choices = defaultdict(str)
        self._movies_choices.update(movie_choices or {})

    @property
    def movie_choices(self) -> Dict[str, str]:
        """Returns user 's movie choices."""
        return self._movies_choices

    def update_movie_choice(self, movie_id: str, choice: str) -> None:
        """Updates the choices for a given user.

        Args:
            movie_id: Id of the movie.
            choice: User choice (i.e., accept, reject).
        """
        self._movies_choices[movie_id] = self._movies_choices[movie_id] + [
            choice
        ]

    def update_movies_choices(self, movies_choices: Dict[str, str]) -> None:
        """Updates the movie choices for a given user.

        Args:
            movies_choices: Dictionary with movie choices (i.e., accept,
              reject).
        """
        self._movies_choices.update(movies_choices)

    def get_movie_choices(self, movie_id: str) -> List[str]:
        """Returns the choices for a given movie.

        Args:
            movie_id: Id of the movie.

        Returns:
            List of previous choices for a movie.
        """
        return self._movies_choices[movie_id]

    def _convert_choice_to_preference(self, choice: str) -> float:
        """Converts a choice to a preference within the range [-1,1].

        Dislike is represented by a preference below 0, while like is
        represented by a preference above 0. If the choice does not express a
        preference (i.e., inquire), then the preference is neutral, i.e., 0.
        Possible choices are: accept, reject, dont_like, inquire, and watched.

        Args:
            choice: Choice (i.e., accept, reject).

        Returns:
            Preference within the range [-1,1].
        """
        if choice == "accept":
            return 1.0
        elif choice in ["reject", "dont_like"]:
            return -1.0

        return 0.0

    def get_tag_preference(
        self, slot: str, tag: str, database: DataBase
    ) -> str:
        """Returns the preference for a given tag (e.g., comedies).

        Args:
            slot: Slot name.
            tag: Tag.
            database: Database with all the movies.

        Returns:
            Tag preference.
        """
        sql_cursor = database.sql_connection.cursor()
        tag_set = sql_cursor.execute(
            f"SELECT ID FROM {database._get_table_name()} WHERE {slot} LIKE '%{tag}%'"
        ).fetchall()

        preference = 0.0
        count_rated = 0
        for movie_id, choices in self._movies_choices.items():
            if movie_id in tag_set:
                # TODO: decide how to handle contradictory choices (e.g., the
                # same movie was accepted and rejected)
                for choice in choices:
                    preference += self._convert_choice_to_preference(choice)
                    count_rated += 1

        return preference / count_rated if count_rated > 0 else 0.0
