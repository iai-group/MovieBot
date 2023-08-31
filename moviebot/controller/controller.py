"""This file contains the Controller which controls the conversation between
the agent and the user."""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from abc import ABC
from collections import defaultdict
from typing import TYPE_CHECKING, Any, DefaultDict, Dict, Type

from dialoguekit.participant import User
from dialoguekit.platforms import Platform as DialogueKitPlatform
from moviebot.connector.dialogue_connector import MovieBotDialogueConnector
from moviebot.core.utterance.utterance import UserUtterance

if TYPE_CHECKING:
    from moviebot.agent.agent import MovieBotAgent


RESTART = "/restart"

logger = logging.getLogger(__name__)


class Controller(DialogueKitPlatform, ABC):
    def __init__(
        self,
        agent_class: Type[MovieBotAgent],
        config: Dict[str, Any] = {},
    ) -> None:
        """Represents a platform.

        Args:
            agent_class: The class of the agent.
            config: Configuration to use. Defaults to empty dict.
        """
        super().__init__(agent_class)

        self._config = config
        self._active_users: DefaultDict[str, User] = defaultdict(User)

    def get_new_agent(self) -> MovieBotAgent:
        """Returns a new instance of the agent.

        Returns:
            Agent.
        """
        return self._agent_class(**self._config)

    def connect(self, user_id: str) -> None:
        """Connects a user to an agent.

        Args:
            user_id: User ID.
        """
        self._active_users[user_id] = User(user_id)
        dialogue_connector = MovieBotDialogueConnector(
            agent=self.get_new_agent(),
            user=self._active_users[user_id],
            platform=self,
        )
        dialogue_connector.start()

    def restart(self, utterance: UserUtterance) -> bool:
        """Returns true if user intent is to restart conversation.

        Args:
            utterance: User utterance.
        """
        return utterance.text == RESTART

    def get_cursor(self) -> sqlite3.Cursor:
        """Returns SQL cursor."""
        db_path = self._config["config"]["DATA"]["db_path"]
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        return c

    def get_user_history_path(self, path: str, user_id: str) -> str:
        """Returns the path to conversation history for a given user.

        Args:
            path: Path to conversation histories.
            user_id: User id.
        """
        return os.path.join(path, f"IAIMovieBot_{user_id}.json")

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
