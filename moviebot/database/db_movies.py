"""This file contains the Database class for IAI MovieBot.

The classes mentioned handle the functionality of query processing for
IAI MovieBot. Currently, the database class is implemented for SQL DB.
"""


import sqlite3
from copy import deepcopy
from typing import Any, Dict, List, Union

from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.annotation.values import Values


class DataBase:
    """DataBase class for SQL databases.

    It provides the functionality to search the database according to
    user preferences.
    """

    def __init__(self, path: str) -> None:
        """Initializes the internal structures of the DataBase class.

        Args:
            path: Path to the database file.
        """
        self.db_file_path = path
        self._initialize_sql()
        self.current_CIN = None
        self.backup_db_results = None

    def _initialize_sql(self) -> None:
        """Initializes the SQL connection and the name of the table to query."""
        self.sql_connection = sqlite3.connect(self.db_file_path)
        self.db_table_name = self._get_table_name()

    def get_sql_condition(
        self, dialogue_state: DialogueState, domain: MovieDomain
    ) -> Union[str, None]:
        """Returns the condition for a SQL query based on dialogue state.

        Args:
            dialogue_state: Dialogue state.
            domain: Domain to check specific parameters.

        Returns:
            SQL condition if there is any.
        """
        if dialogue_state.agent_should_offer_similar:
            similar_movies = list(dialogue_state.similar_movies.values())[0]
            args = [
                f'{Slots.TITLE.value} = "{title}"' for title in similar_movies
            ]
            return " OR ".join(args) if len(args) > 0 else None

        args = []
        for slot, values in dialogue_state.frame_CIN.items():
            if slot not in domain.multiple_values_CIN:
                values = [values]

            args.extend(
                [
                    f"{slot} {self._get_value_for_query(slot, value)}"
                    for value in values
                    if value and value not in set(Values)
                ]
            )

        return " AND ".join(args) if len(args) > 0 else None

    def database_lookup(
        self, dialogue_state: DialogueState, domain: MovieDomain
    ) -> List[Dict[str, Any]]:
        """Performs an SQL query to answer a user requirement.

        Args:
            dialogue_state: The current dialogue state.
            domain: Domain to check specific parameters.

        Returns:
            The results of the SQL query.
        """
        if (
            dialogue_state.isBot
        ):  # restart the SQL connection if the app is running as a
            # client-server app
            self._initialize_sql()

        sql_cursor = self.sql_connection.cursor()
        sql_command = f"SELECT * FROM {self.db_table_name}"
        condition = self.get_sql_condition(dialogue_state, domain)

        if dialogue_state.agent_should_offer_similar and condition is None:
            return []

        if (
            self.current_CIN
            and self.current_CIN == dialogue_state.frame_CIN
            and not dialogue_state.agent_should_offer_similar
        ):
            return self.backup_db_results
        else:
            self.current_CIN = deepcopy(dialogue_state.frame_CIN)

        condition = f"{condition} AND " if condition else ""
        sql_command = (
            f"{sql_command} WHERE {condition}{Slots.RATING.value} > 5 "
            f"ORDER BY {Slots.RATING.value} DESC;"
        )

        query_result = sql_cursor.execute(sql_command).fetchall() or []

        slots = [x[0] for x in sql_cursor.description]
        result = [dict(zip(slots, row)) for row in query_result]

        if not dialogue_state.agent_should_offer_similar:
            self.backup_db_results = result

        return result

    def _get_value_for_query(self, slot: str, value: str) -> str:
        """Converts value to SQL query condition.

        Args:
            slot: Slot the value belongs to.
            value: Slot value.

        Returns:
            String that can be used as a condition in an SQL query.
        """
        if value.startswith(".NOT."):
            value = value.replace(".NOT.", "")
            if slot != Slots.YEAR.value:
                value = f'NOT LIKE "%{value.strip()}%"'
            else:
                if value.startswith(">"):
                    value = value.replace(">", "<")
                elif value.startswith("<"):
                    value = value.replace("<", ">")
                else:
                    value = f"NOT {value}"
        else:
            if slot != Slots.YEAR.value:
                value = f'LIKE "%{value.strip()}%"'
            elif str.isdigit(value[0]):
                value = f"= {value}"
        return value

    def _get_table_name(self) -> str:
        """Gets the SQL database's table name in the database.

        Returns:
            The table name.
        """
        cursor = self.sql_connection.cursor()
        result = cursor.execute(
            "select * from sqlite_master where type = 'table';"
        ).fetchall()

        if result and result[0] and result[0][1]:
            db_table_name = result[0][1]
        else:
            raise ValueError(
                "Dialogue State Tracker cannot specify Table Name from "
                f"database {self.db_file_path}"
            )
        return db_table_name
