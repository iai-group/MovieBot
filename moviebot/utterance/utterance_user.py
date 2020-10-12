"""The user utterance class.
-----------------------------
"""
from moviebot.utterance.utterance import Utterance
from moviebot.nlu.text_processing import TextProcess
from typing import List


class UserUtterance(Utterance):
    """Expands the base class with preprocessed and tokenized version of
    the utterance.
    """

    def get_preprocessed_utterance(self) -> List[str]:
        """Preprocesses the utterance and returns a list of tokens.

        Returns:
            List[str]: List of tokens from the utterance.
        """
        if not hasattr(self, '_preprocessed_utterance'):
            self._preprocessed_utterance = TextProcess().process_text(
                self._utterance)

        return self._preprocessed_utterance
