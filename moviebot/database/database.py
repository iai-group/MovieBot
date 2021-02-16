"""This file contains the Database class for IAI MovieBot. The classes mentioned handle the
functinality of query processing for IAI MovieBot.
Currently, the database class is implemented for SQL DB."""
__author__ = "Javeria Habib"

import sqlite3
from copy import deepcopy

from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.ontology.ontology import Ontology
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.annotation.values import Values


class DataBase:
    """DataBase class for SQL databases. It provides the functionality
    to search the database according to user preferences."""

    def __init__(self, path):
        """Initializes the internal structures of the DataBase class

        Args:
            path: path to the database file

        """
        self.db_file_path = path
        self.sql_connection = sqlite3.connect(
            self.db_file_path, check_same_thread=False)  # SQL connection required to
        # access the database
        self.db_table_name = self._get_table_name()  # name of the table
        self.current_CIN = None
        self.backup_db_results = None

    def database_lookup(self, dialogue_state, ontology):
        """Performs an SQL query to answer a user requirement.

        Args:
            dialogue_state: the current dialogue state
            ontology: ontology to check specific parameters

        Returns:
            the results of the SQL query

        """
        
        if dialogue_state.isBot:  # restart the SQL connection if the app is running as a
            # client-server app
            self.sql_connection = sqlite3.connect(
                self.db_file_path)  # SQL connection required
            # to access the database
            self.db_table_name = self._get_table_name()  # name of the table

        sql_cursor = self.sql_connection.cursor()
        print(f'######{sql_cursor}')
        sql_command = f'SELECT * FROM {self.db_table_name}'
        condition = ''

        if dialogue_state.agent_should_offer_similar:
            args = []
            similar_movies = list(dialogue_state.similar_movies.values())[0]
            if len(similar_movies) > 0:
                for title in similar_movies:
                    args.append(f'{Slots.TITLE.value} = "{title}"')
                condition = ' OR '.join(args) if len(args) > 0 else None
            if len(args) == 0:
                return []  # return no result if nothing similar found
        else:
            args = []
            for slot, values in dialogue_state.frame_CIN.items():
                if slot in ontology.multiple_values_CIN:
                    for value in values:
                        if value and value not in Values.__dict__.values():
                            args.append(slot + ' ' +
                                        self._get_value_for_query(slot, value))
                elif values and values not in Values.__dict__.values():
                    args.append(slot + ' ' +
                                self._get_value_for_query(slot, values))

            condition = ' AND '.join(args) if len(args) > 0 else None

        if self.current_CIN and self.current_CIN == dialogue_state.frame_CIN and not dialogue_state.agent_should_offer_similar:
            return self.backup_db_results
        else:
            self.current_CIN = deepcopy(dialogue_state.frame_CIN)

        if condition:
            sql_command = f'{sql_command} WHERE {condition} AND {Slots.RATING.value} > 5 ORDER BY' \
                          f' {Slots.RATING.value} DESC;'
        else:
            sql_command = f'{sql_command} WHERE {Slots.RATING.value} > 5 ORDER BY' \
                          f' {Slots.RATING.value} DESC;'

        # print(sql_command)
        query_result = sql_cursor.execute(sql_command).fetchall()

        # query_result, remove_title_from_CIN = self._remove_title_from_CIN(query_result,
        # condition, args)

        slots = [x[0] for x in sql_cursor.description]
        result = []
        if query_result:
            for row in query_result:
                result.append(dict(zip(slots, row)))

        if not dialogue_state.agent_should_offer_similar:
            self.backup_db_results = result

        return result  # , remove_title_from_CIN

    def _remove_title_from_CIN(self, query_result, condition, args):
        """

        Args:
            query_result: 
            condition: 
            args: 

        """
        # extra check that name can be misleading
        remove_title_from_CIN = False
        if len(query_result) == 0 and any(
            [arg.startswith(Slots.TITLE.vlaue) for arg in args]):
            condition = ' AND '.join([
                arg for arg in args if not arg.startswith(Slots.TITLE.vlaue)
            ]) if len(args) > 0 else None
            sql_cursor = self.sql_connection.cursor()
            sql_command = f'SELECT * FROM {self.db_table_name}'
            if condition:
                sql_command = f'{sql_command} WHERE {condition} ORDER BY {Slots.RATING.value} DESC;'
            else:
                sql_command = f'{sql_command} ORDER BY {Slots.RATING.value} DESC;'
            query_result = sql_cursor.execute(sql_command).fetchall()
            if len(query_result) > 0:
                remove_title_from_CIN = True
        return query_result, remove_title_from_CIN

    def _get_value_for_query(self, slot, value):
        """

        Args:
            slot: 
            value: 

        """
        if value.startswith('.NOT.'):
            value = value.replace('.NOT.', '')
            if slot != Slots.YEAR.value:
                value = f'NOT LIKE "%{value.strip()}%"'
            else:
                if value.startswith('>'):
                    value = value.replace('>', '<')
                elif value.startswith('<'):
                    value = value.replace('<', '>')
                else:
                    value = f'NOT {value}'
        else:
            if slot != Slots.YEAR.value:
                value = f'LIKE "%{value.strip()}%"'
            elif str.isdigit(value[0]):
                value = f'= {value}'
        return value

    def _get_table_name(self):
        """Gets the SQL database's table name in the database
        
        Returns:
            the table name
        """
        cursor = self.sql_connection.cursor()
        result = cursor.execute("select * from sqlite_master "
                                "where type = 'table';").fetchall()

        if result and result[0] and result[0][1]:
            db_table_name = result[0][1]
        else:
            raise ValueError(
                'Dialogue State Tracker cannot specify Table Name from '
                'database {0}'.format(self.db_file_path))
        return db_table_name
