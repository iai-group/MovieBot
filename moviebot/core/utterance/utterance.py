"""Utterance classes
====================

Classes that contain basic information about the utterance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import List

from dialoguekit.core import Utterance
from dialoguekit.participant import DialogueParticipant
from moviebot.nlu.text_processing import Token, Tokenizer


@dataclass(eq=True, unsafe_hash=True)
class UserUtterance(Utterance):
    """Expands the base class with preprocessed and tokenized version of
    the utterance.
    """

    participant: DialogueParticipant = DialogueParticipant.USER

    def get_tokens(self) -> List[Token]:
        """Preprocesses the utterance and returns a list of tokens.

        Returns:
            List[Token]: List of tokens from the utterance.
        """
        if not hasattr(self, "_tokens"):
            self._tokens = Tokenizer().process_text(self.text)

        return self._tokens

    @classmethod
    def from_utterance(cls, utterance: Utterance) -> UserUtterance:
        """Creates a new user utterance from an existing utterance.

        Args:
            utterance: Utterance.

        Returns:
            UserUtterance: User utterance.
        """
        args = asdict(utterance)
        return cls(**args)


@dataclass(eq=True, unsafe_hash=True)
class AgentUtterance(Utterance):
    """Expands the base class to automatically set the participant as agent."""

    participant: DialogueParticipant = DialogueParticipant.AGENT
