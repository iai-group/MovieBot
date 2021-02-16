"""This file contains the list of possible intents for user as constants.
This approach will help the NLU to identify the intents from a limited set
without making a mistake."""

__author__ = 'Javeria Habib'

from enum import Enum


class UserIntents(Enum):
    """This class contains the list of possible intents for user as constants.
    This approach will help the NLU to identify the intents from a pre-defined
    set."""

    REVEAL = 'reveal'

    INQUIRE = 'inquire'
    REMOVE_PREFERENCE = 'remove_preference'

    REJECT = 'reject'
    ACCEPT = 'accept'

    CONTINUE_RECOMMENDATION = 'continue_recommendation'
    RESTART = 'restart'

    UNK = 'UNK'
    ACKNOWLEDGE = 'acknowledge'
    DENY = 'deny'
    HI = 'hi'
    BYE = 'bye'

    def __str__(self):
        return self.value
