"""Record all the details of each dialogue in the conversation in it's raw form.
If required, it also saves the dialogue acts.
"""

__author__ = "Javeria Habib"

import json
import os


class RecorderBot:
    """Record all the details of each dialogue in the conversation in it's raw form.
    If required, it also saves the dialogue acts."""

    def __init__(self, history_folder):
        """Initializes the Recorder

        Args:
            history_folder: Path where the file must be saved

        """
        if os.path.isdir(history_folder):
            self.path = history_folder
        else:
            raise FileNotFoundError(
                'History path "{}" not found.'.format(history_folder)
            )
        self.user_context = {}
        self.previous_dialogue_record = {}

    def record_user_data(self, user_id, record_data):
        """Records the current dialogue utterance for the user

        Args:
            user_id: Id of the use
            record_data:

        """
        user_history_path = self.path + "user_" + user_id + ".json"
        if not os.path.isfile(user_history_path):
            self.create_record(user_id, user_history_path, record_data)
        else:
            self.update_record(user_id, user_history_path, record_data)

    def update_record(self, user_id, record_path, record_data):
        """Update an already existing json file

        Args:
            user_id: Id of the user
            record_path: path to the json fil
            record_data:

        """
        with open(record_path) as hist_file:
            data = json.load(hist_file)
        data.append(record_data)
        with open(record_path, "w") as hist_file:
            json.dump(data, hist_file, indent=4)

    def create_record(self, user_id, record_path, record_data):
        """Saves all the dialogues in the conversation to a file

        Args:
            user_id: Id of the user
            record_path: path to the json fil
            record_data:

        """
        with open(record_path, "w") as hist_file:
            json.dump([record_data], hist_file, indent=4)

    def load_user_data(self, user_id):
        """Loads the previously saved conversation log

        Args:
            user_id: Id of the user

        """
        user_history_path = self.path + "user_" + user_id + ".json"
        if os.path.isfile(user_history_path):
            with open(user_history_path) as hist_file:
                user_context = json.load(hist_file)
                return user_context

    """ This part of the code is a backup in case we need to store all data in one place"""

    def initialize_bot_data(self, bot_id, user_id, context):
        """Initialize the recording parameters for a specific user_id

        Args:
            bot_id: bot ID
            user_id: user ID
            context: context of the conversation

        Returns:
            the dialogue record to be added to context

        """
        if "previous_dialogue_record" in context.bot_data:
            self.previous_dialogue_record = context.bot_data[
                "previous_dialogue_record"
            ]
        if bot_id not in self.previous_dialogue_record:
            self.previous_dialogue_record[bot_id] = {}
            print(f"bot_id added: {bot_id}")
        if user_id not in self.previous_dialogue_record:
            self.previous_dialogue_record[bot_id][user_id] = None
        return self.previous_dialogue_record

    def record_bot_data(self, bot_id, user_id, record_data):
        """Records the current dialogue utterance

        Args:
            bot_id: Id of the bot
            user_id: Id of the use
            record_data:

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
        bot_history_path = self.path + "bot_" + bot_id + ".json"
        if not os.path.isfile(bot_history_path):
            self.create_record(bot_id, bot_history_path, record)
        else:
            self.update_record(bot_id, bot_history_path, record)
        # update the previous record
        self.previous_dialogue_record[bot_id][user_id] = record_data
