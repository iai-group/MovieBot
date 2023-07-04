"""This file contains the main functions for loading database and tag_words
files for NLU."""

import json
import logging
import os
from typing import Any, Dict

from tqdm import tqdm

from moviebot.database.database import DataBase
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.text_processing import Tokenizer
from moviebot.ontology.ontology import Ontology

DEFAULT_SLOT_VALUE_PATH = "data/slot_values.json"

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(
        self,
        config: Dict[str, Any],
    ) -> None:
        """DataLoader class loads the database as slot-value pairs and the
        tag-words for slots.

        This data will be used by NLU to check user intents.

        Args:
            config: Dictionary containing configuration.
        """
        self.ontology: Ontology = config["ontology"]
        self.database: DataBase = config["database"]
        self.slot_values_path = (
            config["slot_values_path"] or DEFAULT_SLOT_VALUE_PATH
        )

    def load_tag_words(self, file_path: str) -> Dict[str, Any]:
        """Loads the tag words for the path provided. This can be for the slots
        in the database or the patterns.

        Args:
            file_path: The path to the input json file.

        Raises:
            FileNotFoundError: If the file does not exist.

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

    def save_slot_value_pairs(self, slot_values: Dict[str, Any]) -> None:
        """Saves slot-value pairs to a file.

        Args:
            slot_values: Dictionary of slot-value(s) pairs.
        """
        with open(self.slot_values_path, "w") as slot_val_file:
            logger.info(f"Writing slot-value pairs to {self.slot_values_path}")
            json.dump(slot_values, slot_val_file, indent=4)

    def _get_all_data_from_database(self) -> Dict[str, Any]:
        """Gets all the data from the database.

        Returns:
            Dictionary of data from the database.
        """
        cursor = self.database.sql_connection.cursor()
        columns = ",".join(self.ontology.slots_annotation)
        all_data = cursor.execute(
            f"Select {columns} from {self.database.db_table_name};"
        ).fetchall()
        return all_data

    def _generate_slot_value_pairs(self) -> Dict[str, Any]:
        """Loads the database to fill dialogue slots with a list of possible
        slot_values.

        Returns:
            Dictionary of slot-value(s) pairs.
        """
        tokenizer = Tokenizer()
        slot_values = {
            slot: {} if slot != Slots.YEAR.value else []
            for slot in self.ontology.slots_annotation
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
        all_data = self._get_all_data_from_database()
        logger.info("Loading the database......")
        for row in tqdm(all_data):
            for slot, value in zip(self.ontology.slots_annotation, row):
                if slot in multi_slots:
                    temp_result = [x.strip() for x in value.split(",")]
                    if slot == Slots.GENRES.value:
                        temp_result = [x.lower() for x in temp_result]
                    slot_values[slot].update(
                        {
                            temp_value: tokenizer.lemmatize_text(temp_value)
                            for temp_value in temp_result
                            if temp_value not in slot_values[slot]
                        }
                    )
                elif value not in slot_values[slot]:
                    if slot == Slots.YEAR.value:
                        slot_values[slot].append(value)
                    else:
                        slot_values[slot].update(
                            {value: tokenizer.lemmatize_text(value)}
                        )

        self.save_slot_value_pairs(slot_values)
        return slot_values
