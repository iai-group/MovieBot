"""Records the dialogue details of the conversation in it's raw form."""


import json
import os
from typing import Any, Dict, List

RecordData = Dict[str, Any]


class RecorderBot:
    def __init__(self, history_folder: str) -> None:
        """Initializes the Recorder.

        If required, it also saves the dialogue acts.

        Args:
            history_folder: Path to the save file.
        """
        if os.path.isdir(history_folder):
            self.path = history_folder
        else:
            raise FileNotFoundError(
                f"History path '{history_folder}' not found."
            )
        self.user_context = {}
        self.previous_dialogue_record = {}

    def get_user_history_path(self, user_id: str) -> str:
        """Returns full path to the conversation log for user.

        Args:
            user_id: User ID.
        """
        return os.path.join(self.path, f"user_{user_id}.json")

    def record_user_data(self, user_id: str, record_data: RecordData) -> None:
        """Records the current dialogue utterance for the user.

        Args:
            user_id: Id of the user.
            record_data: Dictionary with data to record.
        """
        user_history_path = self.get_user_history_path(user_id)
        if not os.path.isfile(user_history_path):
            self._create_record(user_history_path, record_data)
        else:
            self._update_record(user_history_path, record_data)

    def _create_record(self, record_path: str, record_data: RecordData) -> None:
        """Creates a new record and saves record_data.

        Args:
            record_path: Path to the json file.
            record_data: Dictionary with data to record.
        """
        with open(record_path, "w") as hist_file:
            json.dump([record_data], hist_file, indent=4)

    def _update_record(self, record_path: str, record_data: RecordData) -> None:
        """Updates an already existing record file.

        Args:
            record_path: Path to the json file.
            record_data: Dictionary with data to record.
        """
        with open(record_path) as hist_file:
            data: List[RecordData] = json.load(hist_file)
        data.append(record_data)
        with open(record_path, "w") as hist_file:
            json.dump(data, hist_file, indent=4)

    def load_user_data(self, user_id: str) -> List[RecordData]:
        """Loads the previously saved conversation log.

        Args:
            user_id: Id of the user.

        Returns:
            List of records (i.e., conversation turns).
        """
        user_history_path = self.get_user_history_path(user_id)
        if os.path.isfile(user_history_path):
            with open(user_history_path) as hist_file:
                user_context = json.load(hist_file)
                return user_context

    """ This part of the code is a backup in case we need to store all data
    in one place."""

    def initialize_bot_data(
        self, bot_id: str, user_id: str, context: RecordData
    ):
        """Initializes the recording parameters for a specific user_id.

        Args:
            bot_id: bot ID.
            user_id: user ID.
            context: Context of the conversation.

        Returns:
            The dialogue record to be added to context.
        """
        if "previous_dialogue_record" in context.bot_data:
            self.previous_dialogue_record = context.bot_data[
                "previous_dialogue_record"
            ]
        if bot_id not in self.previous_dialogue_record:
            self.previous_dialogue_record[bot_id] = {}
            print(f"bot_id added: {bot_id}")
        if user_id not in self.previous_dialogue_record[bot_id]:
            self.previous_dialogue_record[bot_id][user_id] = None
        return self.previous_dialogue_record

    def record_bot_data(
        self, bot_id: str, user_id: str, record_data: RecordData
    ) -> None:
        """Records the current dialogue utterance.

        Args:
            bot_id: Bot ID.
            user_id: User ID.
            record_data: Dictionary with data to record.
        """
        previous_record = self.previous_dialogue_record[bot_id][user_id]
        if not previous_record:
            # update the previous record
            self.previous_dialogue_record[bot_id][user_id] = record_data
            return
        record = {
            "User_ID": user_id,
            "Previous_State": self.previous_dialogue_record[bot_id][user_id],
            "Current_State": record_data,
        }
        bot_history_path = os.path.join(self.path, f"bot_{bot_id}.json")
        if not os.path.isfile(bot_history_path):
            self._create_record(bot_history_path, record)
        else:
            self._update_record(bot_history_path, record)
        # update the previous record
        self.previous_dialogue_record[bot_id][user_id] = record_data
