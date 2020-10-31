"""Utterance classes
=======================

Classes that contain basic information about the utterance.
"""
from typing import Text, List, Dict, Any
from abc import ABC
import datetime

from moviebot.nlu.text_processing import Token, TextProcess


class Utterance(ABC):
    """This is an abstract class for storing utterances. It contains
    relevant information about the utterance like what was said, who said
    it and when.
    """

    def __init__(self, message: Dict[Text, Any]) -> None:
        """Initializes the Utterance class with an utterance and a timestamp.

        Args:
            message (Dict[Text, Any]): Dictionary should contain text and date
                fields.

        """
        self._utterance = message.get('text', '')
        self._timestamp = message.get('date', self._set_timestamp())

    def get_source(self) -> Text:
        """Returns the name of the inherited class which represents the source
        of the utterance.

        Returns:
            str: Name of the source class.
        """
        return self.__class__.__name__

    def get_text(self) -> Text:
        return self._utterance

    def get_timestamp(self) -> Text:
        return str(self.timestamp)

    def _set_timestamp(self):
        return datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return '{} - {}:\n\t{}'.format(
            self.get_timestamp(),
            self.get_source(),
            self.get_text(),
        )


class UserUtterance(Utterance):
    """Expands the base class with preprocessed and tokenized version of
    the utterance.
    """

    def get_tokens(self) -> List[Token]:
        """Preprocesses the utterance and returns a list of tokens.

        Returns:
            List[Token]: List of tokens from the utterance.
        """
        if not hasattr(self, '_tokens'):
            self._tokens = TextProcess().process_text(self._utterance)

        return self._tokens


class AgentUtterance(Utterance):
    """Stores the utterance that the agent returns.
    """
    pass
