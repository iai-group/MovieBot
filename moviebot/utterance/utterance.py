"""Utterance classes
=======================

Classes that contain basic information about the utterance.
"""
from typing import Text, List
from abc import ABC
import datetime

from moviebot.nlu.text_processing import Token, TextProcess


class Utterance(ABC):
    """This is an abstract class for storing utterances. It contains
    relevant information about the utterance like what was said, who said
    it and when.
    """

    def __init__(self, utterance: Text, timestamp: Text = None):
        """Initializes the Utterance class with an utterance and a timestamp.

        Args:
            utterance (str): The string to store as utterance
            timestamp (str, optional): Timestamp of the utterance. It is set to
                the time of initialization if not provided.
        """
        self.utterance = utterance
        self.timestamp = self._set_timestamp(timestamp)

    def source(self) -> Text:
        """Returns the name of the inherited class which represents the source
        of the utterance.

        Returns:
            str: Name of the source class.
        """
        return self.__class__.__name__

    def _set_timestamp(self, timestamp: Text = None):
        return timestamp if timestamp else str(
            datetime.datetime.now(datetime.timezone.utc))

    def __str__(self):
        return '{} - {}:\n\t{}'.format(
            self.timestamp,
            self.source(),
            self.utterance,
        )


class UserUtterance(Utterance):
    """Expands the base class with preprocessed and tokenized version of
    the utterance.
    """

    def get_tokens(self) -> List[Token]:
        """Preprocesses the utterance and returns a list of tokens.

        Returns:
            List[str]: List of tokens from the utterance.
        """
        if not hasattr(self, '_tokens'):
            self._tokens = TextProcess().process_text(self.utterance)

        return self._tokens


class AgentUtterance(Utterance):
    """Stores the utterance that the agent returns.
    """
    pass
