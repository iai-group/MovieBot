"""This file contains the main functions for loading database and tag_words
files for NLU."""


import json
import os

from moviebot.nlu.annotation.slots import Slots


class DataLoader:
    """LoadData class loads the database as slot-value pairs and the tag-words
    for slots.

    This data will be used by NLU to check user intents.
    """

    def __init__(self, config, _lemmatize_value):
        """Initializes the data loader and load database, tag words etc.

        :type self.database: DataBase
        :type self.ontology: Ontology

        Args:
            config:
            _lemmatize_value:
        """
        self.ontology = config["ontology"]
        self.database = config["database"]
        self.slot_values_path = config["slot_values_path"]
        self.lemmatize_value = _lemmatize_value

    def load_tag_words(self, file_path: str):
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
                'File "{}" for tag words not found.'.format(file_path)
            )
        return tag_words

    def _convert_values_to_set(self, slot_values):
        """

        Args:
            slot_values:

        """
        for slot, values in slot_values.items():
            if isinstance(values, dict):
                slot_values[slot] = set(values.keys())
            else:
                slot_values[slot] = set(values)

    def load_database(self):  # noqa: C901
        """Loads the database to fill dialogue slots with a list of possible
        slot_values. This can be used further to understand what user intends
        to ask.

        Returns:
            Slot values pairs.
        """
        if self.slot_values_path and os.path.isfile(self.slot_values_path):
            with open(self.slot_values_path) as slot_val_file:
                slot_values = json.load(slot_val_file)
            # self._convert_values_to_set(slot_values)
            return slot_values
        # else load slot_values from database
        cursor = self.database.sql_connection.cursor()
        db_table_name = self.database.db_table_name
        slot_values = {}
        all_data = cursor.execute(
            "Select * from " + db_table_name + ";"
        ).fetchall()
        total_count = round(len(all_data), -2)
        print_count = int(total_count / 4)
        self.slots = [
            x[0] for x in cursor.description if x[0] != Slots.ID.value
        ]
        count = 0
        print("Loading the database......")
        for row in all_data:
            slot_value_pair = dict(zip(self.slots, row[1:]))
            count += 1
            for slot, value in slot_value_pair.items():
                if slot not in self.ontology.slots_annotation:
                    continue
                if slot not in slot_values:
                    slot_values[slot] = {} if slot != Slots.YEAR.value else []
                if slot in [
                    x.value
                    for x in [
                        Slots.GENRES,
                        Slots.KEYWORDS,
                        Slots.ACTORS,
                        Slots.DIRECTORS,
                    ]
                ]:
                    if slot not in slot_values:
                        slot_values[slot] = {}
                    temp_result = [x.strip() for x in value.split(",")]
                    if slot == Slots.GENRES.value:
                        temp_result = [x.lower() for x in temp_result]
                    for temp_value in temp_result:
                        if temp_value not in slot_values[slot]:
                            slot_values[slot].update(
                                {temp_value: self.lemmatize_value(temp_value)}
                            )
                else:
                    if value not in slot_values[slot]:
                        if slot == Slots.YEAR.value:
                            slot_values[slot].append(value)
                        else:
                            slot_values[slot].update(
                                {value: self.lemmatize_value(value)}
                            )
            if count % print_count == 0:
                print(f"{int(100 * count / total_count)}% data is loaded.")
        if not self.slot_values_path:
            self.slot_values_path = "data_and_config/data/slot_values.json"
        with open(self.slot_values_path, "w") as slot_val_file:
            print(f"Writing loaded database to {self.slot_values_path}")
            json.dump(slot_values, slot_val_file, indent=4)
        return slot_values
