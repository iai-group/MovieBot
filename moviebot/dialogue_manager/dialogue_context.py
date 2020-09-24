"""DialogueContext models a record of previous conversation.
It keeps track of the recommendations agent made with user response to those recommendations.
"""

__author__ = "Javeria Habib"


class DialogueContext:
    """DialogueContext models a record of previous conversation. It keeps track of
    the recommendations agent made with user response to those recommendations."""

    def __init__(self):
        """Initializes the basic parameters of the context"""
        self.movies_recommended = {}

    def initialize(self, previous_recommendation={}):
        """Initialize the dialogue context by loading previous context

        Args:
            previous_recommendation:  (Default value = {})

        """
        self.movies_recommended = {}
        # self.movies_recommended.update(previous_recommendation)

    def __str__(self):
        return str(self.movies_recommended)
