"""DialogueContext models a record of previous conversation.

It keeps track of the recommendations agent made with user response to
those recommendations. In addition, it keeps track of all previous
utterances from both the user and the agent.
"""


from moviebot.core.utterance.utterance import Utterance


class DialogueContext:
    def __init__(self) -> None:
        """Initializes the basic parameters of the context."""
        self.movies_recommended = {}
        self.previous_utterances = []

    def initialize(self) -> None:
        """Initializes the dialogue context."""
        self.movies_recommended = {}
        self.previous_utterances = []

    def add_utterance(self, utterance: Utterance) -> None:
        """Adds an utterance to the context.

        Args:
            utterance: Utterance to add.
        """
        self.previous_utterances.append(utterance)

    def __str__(self) -> str:
        """Returns the string representation of the movies recommended."""
        return str(self.movies_recommended)
