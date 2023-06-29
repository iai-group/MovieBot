"""This file contains the Controller which controls the conversation between
the agent and the user."""

import json
import logging
import os
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict

from moviebot.agent.agent import Agent
from moviebot.core.utterance.utterance import UserUtterance

RESTART = "/restart"

logger = logging.getLogger(__name__)


class Controller(ABC):
    def __init__(self, configuration: Dict[str, Any]):
        """This is the main class that controls the other components of the
        IAI MovieBot. The controller executes the conversational agent.

        Args:
            configuration: the settings for the agent
        """
        self.configuration = configuration

    @abstractmethod
    def execute_agent(self):
        """Runs the conversational agent and executes the dialogue by calling
        the basic components of IAI MovieBot.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def initialize_agent(self) -> Agent:
        """Initializes and returns an agent based on configuration."""
        agent = Agent(self.configuration)
        logger.debug(
            "The components for the conversation are initialized successfully."
        )
        return agent

    def restart(self, utterance: UserUtterance) -> bool:
        """Returns true if user intent is to restart conversation.

        Args:
            utterance: User utterance.
        """
        return utterance.text == RESTART

    def get_cursor(self) -> sqlite3.Cursor:
        """Returns SQL cursor."""
        conn = sqlite3.connect(self.configuration["DATA"]["db_path"])
        c = conn.cursor()
        return c

    def get_user_history_path(self, path: str, user_id: str) -> str:
        """Returns the path to conversation history for a given user.

        Args:
            path: Path to conversation histories.
            user_id: User id.
        """
        return os.path.join(path, f"user_{user_id}.json")

    def load_user_data(self, path: str, user_id: str) -> Dict[str, Any]:
        """Loads movie choices (accept/reject) for a user from conversation
        history.

        Args:
            path: Path to conversation histories.
            user_id: User id.

        Returns:
            Object with previous movie choices.
        """
        user_history_path = self.get_user_history_path(path, user_id)
        loaded_data = {}
        if os.path.isfile(user_history_path):
            with open(user_history_path) as json_file:
                data = json.load(json_file)
                for conversation in data:
                    for movie in conversation["Context"]:
                        loaded_data[movie] = conversation["Context"][movie]
        return loaded_data

    def delete_history(self, path: str, user_id: str) -> bool:
        """Deletes stored conversation history for user.

        Args:
            path: Path to conversation histories.
            user_id: User id.

        Returns:
            A boolean indicating whether or not history was deleted.
        """
        user_history_path = self.get_user_history_path(path, user_id)
        if os.path.isfile(user_history_path):
            os.remove(user_history_path)
            return True
        return False
