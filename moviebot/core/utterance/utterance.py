"""Utterance classes
=======================

Classes that contain basic information about the utterance.
"""
import datetime
from abc import ABC
from typing import Any, Dict, List

from moviebot.nlu.text_processing import Token, Tokenizer


class Utterance(ABC):
    def __init__(self, message: Dict[str, Any]) -> None:
        """This is an abstract class for storing utterances.

        The class contains relevant information about the utterance like what
        was said, who said it and when.

        Args:
            message: Dictionary should contain text and date fields.
        """
        self._utterance = message.get("text", "")
        self._timestamp = self._set_timestamp(message.get("date"))

    def get_source(self) -> str:
        """Returns the name of the inherited class which represents the source
        of the utterance.

        Returns:
            Name of the source class.
        """
        return self.__class__.__name__

    def get_text(self) -> str:
        """Returns raw utterance text."""
        return self._utterance

    def get_timestamp(self) -> str:
        """Returns utterance timestamp in string format."""
        return str(self._timestamp)

    def _set_timestamp(self, timestamp: int = None) -> datetime.datetime:
        """Create new datetime object from timestamp.

        If timestamp is None, generates new datetime object with current time.

        Args:
            timestamp: Timestamp when the message was created.

        Returns:
            Datetime object from timestamp.
        """
        if timestamp:
            return datetime.datetime.fromtimestamp(timestamp)
        return datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return "{} - {}:\n\t{}".format(
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
        if not hasattr(self, "_tokens"):
            self._tokens = Tokenizer().process_text(self._utterance)

        return self._tokens


class AgentUtterance(Utterance):
    """Stores the utterance that the agent returns."""

    pass
