"""Create a human user for the dialogue environment."""

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.user import User


class HumanUser(User):
    def __init__(self) -> None:
        """Initializes human user."""
        super().__init__(id="HumanUser")

    def initialize(self) -> None:
        """Initializes the user if the game starts again.

        This method is not used.
        """
        pass

    def receive_utterance(self, utterance: Utterance) -> Utterance:
        """Receives an agent utterance.

        Args:
            utterance: Agent utterance.

        Returns:
            User utterance.
        """
        print(f"Agent utterance: {utterance.text}")
        text = input("Enter your action: ")
        return AnnotatedUtterance(
            text=text,
            participant=self._user_type,
        )
