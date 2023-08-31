"""This file contains the main functions for loading database and tag_words
files for NLU."""

import json
import logging
import os
from typing import Any, Callable, Dict

from moviebot.database.db_movies import DataBase
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlu.annotation.slots import Slots

DEFAULT_SLOT_VALUE_PATH = "data/slot_values.json"

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(
        self,
        config: Dict[str, Any],
        lemmatize_value: Callable[[str, bool], str],
    ) -> None:
        """DataLoader class loads the database as slot-value pairs and the
        tag-words for slots.

        This data will be used by NLU to check user intents.

        Args:
            config: Dictionary containing configuration.
            lemmatize_value: Function for lemmatization.
        """
        self.domain: MovieDomain = config["domain"]
        self.database: DataBase = config["database"]
        self.slot_values_path = (
            config["slot_values_path"] or DEFAULT_SLOT_VALUE_PATH
        )
        self.lemmatize_value = lemmatize_value

    def load_tag_words(self, file_path: str) -> Dict[str, Any]:
        """Loads the tag words for the path provided. This can be for the slots
        in the database or the patterns.

        Args:
            file_path: The path to the input json file.

        Returns:
            The output dictionary extracted from the file.
        """
        if os.path.isfile(file_path):
            with open(file_path) as file:
                tag_words = json.load(file)
        else:
            raise FileNotFoundError(
                f"File '{file_path}' for tag words not found."
            )
        return tag_words

    def load_slot_value_pairs(self) -> Dict[str, Any]:
        """Loads slot-value pairs from a file.

        If the file does not exist, it generates slot-value pairs from
        database.

        Returns:
            Dictionary of slot-value(s) pairs.
        """
        if os.path.isfile(self.slot_values_path):
            with open(self.slot_values_path) as slot_val_file:
                slot_values = json.load(slot_val_file)
        else:
            slot_values = self._generate_slot_value_pairs()
        return slot_values

    def _generate_slot_value_pairs(self) -> Dict[str, Any]:
        """Loads the database to fill dialogue slots with a list of possible
        slot_values.

        Returns:
            Dictionary of slot-value(s) pairs.
        """
        cursor = self.database.sql_connection.cursor()
        db_table_name = self.database.db_table_name
        columns = ",".join(self.domain.slots_annotation)
        all_data = cursor.execute(
            f"Select {columns} from {db_table_name};"
        ).fetchall()
        total_count = round(len(all_data), -2)
        print_count = int(total_count / 4)
        slot_values = {
            slot: {} if slot != Slots.YEAR.value else []
            for slot in self.domain.slots_annotation
        }
        multi_slots = {
            x.value
            for x in [
                Slots.GENRES,
                Slots.KEYWORDS,
                Slots.ACTORS,
                Slots.DIRECTORS,
            ]
        }

        logger.info("Loading the database......")
        for count, row in enumerate(all_data):
            for slot, value in zip(self.domain.slots_annotation, row):
                if slot in multi_slots:
                    temp_result = [x.strip() for x in value.split(",")]
                    if slot == Slots.GENRES.value:
                        temp_result = [x.lower() for x in temp_result]
                    slot_values[slot].update(
                        {
                            temp_value: self.lemmatize_value(temp_value)
                            for temp_value in temp_result
                            if temp_value not in slot_values[slot]
                        }
                    )
                elif value not in slot_values[slot]:
                    if slot == Slots.YEAR.value:
                        slot_values[slot].append(value)
                    else:
                        slot_values[slot].update(
                            {value: self.lemmatize_value(value)}
                        )
            if (count + 1) % print_count == 0:
                logger.info(
                    f"{int(100 * (count+1) / total_count)}% data is loaded."
                )

        with open(self.slot_values_path, "w") as slot_val_file:
            logger.info(f"Writing loaded database to {self.slot_values_path}")
            json.dump(slot_values, slot_val_file, indent=4)
        return slot_values
