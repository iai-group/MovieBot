"""This file contains the Controller which controls the conversation between
the agent and the user."""

import logging
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
        """
        raise NotImplementedError

    def initialize_agent(self) -> Agent:
        """Initializes and returns an agent based on configuration."""
        agent = Agent(self.configuration)
        agent.initialize()
        logger.debug(
            "The components for the conversation are initialized successfully."
        )
        return agent

    def restart(self, utterance: UserUtterance) -> bool:
        """Returns true if user intent is to restart conversation.

        Args:
            utterance: User utterance.
        """
        return utterance.get_text() == RESTART
