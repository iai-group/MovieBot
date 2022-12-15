"""This file contains the Controller which controls the conversation between
the agent and the user."""

__author__ = "Javeria Habib"

from abc import ABC, abstractmethod


class Controller(ABC):
    """This is the main class that controls the other components of the
    IAI MovieBot. The controller executes the conversational agent."""

    def __init__(self):
        """Initializes some basic structs for the Controller."""

    @abstractmethod
    def execute_agent(self, configuration):
        """Runs the conversational agent and executes the dialogue by calling
        the basic components of IAI MovieBot

        Args:
            configuration: the settings for the agent

        """
        pass
