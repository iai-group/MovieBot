"""Utterance abstract class.
------------------------------
"""
from abc import ABC
import datetime


class Utterance(ABC):
    """This is an abstract class for storing utterances. It contains
    relevant information about the utterance like what was said, who said
    it and when.
    """

    def __init__(self, utterance: str, timestamp: str = None):
        """Initializes the Utterance class with an utterance and a timestamp.

        Args:
            utterance (str): The string to store as utterance
            timestamp (str, optional): Timestamp of the utterance. It is set to
                the time of initialization if not provided.
        """
        self._utterance = utterance
        self._timestamp = self._set_timestamp(timestamp)

    def utterance(self) -> str:
        """Returns the original utterance.

        Returns:
            str: The original utterance
        """
        return self._utterance

    def timestamp(self) -> str:
        """Returns the timestamp of the utterance.

        Returns:
            str: timestamp
        """
        return self._timestamp

    def source(self) -> str:
        """Returns the name of the inherited class which represents the source
        of the utterance.

        Returns:
            str: Name of the source class.
        """
        return self.__class__.__name__

    def _set_timestamp(self, timestamp: str = None):
        return timestamp if timestamp else str(
            datetime.datetime.now(datetime.timezone.utc))

    def __str__(self):
        return '{} - {}:\n\t{}'.format(
            self.timestamp(),
            self.source(),
            self.utterance(),
        )
