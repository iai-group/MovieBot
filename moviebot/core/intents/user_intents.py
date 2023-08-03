"""This file contains the list of possible intents for user as constants.
This approach will help the NLU to identify the intents from a limited set
without making a mistake."""


from enum import Enum

from dialoguekit.core import Intent


class UserIntents(Enum):
    """This class contains the list of possible intents for user as constants.
    This approach will help the NLU to identify the intents from a pre-defined
    set."""

    REVEAL = Intent("reveal")

    INQUIRE = Intent("inquire")
    REMOVE_PREFERENCE = Intent("remove_preference")

    REJECT = Intent("reject")
    ACCEPT = Intent("accept")

    CONTINUE_RECOMMENDATION = Intent("continue_recommendation")
    RESTART = Intent("restart")

    UNK = Intent("UNK")
    ACKNOWLEDGE = Intent("acknowledge")
    DENY = Intent("deny")
    HI = Intent("hi")
    BYE = Intent("bye")
