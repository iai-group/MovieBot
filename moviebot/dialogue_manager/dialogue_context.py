"""DialogueContext models a record of previous conversation.

It keeps track of the recommendations agent made with user response to
those recommendations. In addition, it keeps track of all previous
utterances from both the user and the agent.
"""


from moviebot.core.utterance.utterance import Utterance


class DialogueContext:
    def __init__(self):
        """Initializes the basic parameters of the context."""
        self.movies_recommended = {}
        self.previous_utterances = []

    def initialize(self, previous_recommendation={}):
        """Initializes the dialogue context by loading previous context.

        Args:
            previous_recommendation: Set with previous recommendations.
              Defaults to empty set.
        """
        self.movies_recommended = {}
        self.previous_utterances = []
        # self.movies_recommended.update(previous_recommendation)

    def add_utterance(self, utterance: Utterance) -> None:
        """Adds an utterance to the context.

        Args:
            utterance: Utterance to add.
        """
        self.previous_utterances.append(utterance)

    def __str__(self) -> str:
        """Returns the string representation of the movie recommended."""
        return str(self.movies_recommended)
