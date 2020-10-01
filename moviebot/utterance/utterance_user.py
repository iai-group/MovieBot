"""This file contains the user utterance. In addition to the raw utterance
this class stores the preprocessed utterance as well.
"""
from moviebot.utterance.utterance import Utterance


class UserUtterance(Utterance):
    """Expands the base class with preprocessed and tokenized version of
    the utterance 
    """

    def get_preprocessed_utterance(self):
        # TODO(Ivica Kostric): make logic for preprocessing.
        return self.utterance().split()