"""This file contains the list of possible intents for agent/system as
constants. This approach will help the Dialogue Policy to decide the intents
from a pre-defined set."""

__author__ = "Javeria Habib"

from enum import Enum


class AgentIntents(Enum):
    """This class contains the list of possible intents for agent/system as
    constants. This approach will help the Dialogue Policy to decide the intents
    from a pre-defined set."""

    ELICIT = "elicit"

    # When agent has results
    RECOMMEND = "recommend"
    NO_RESULTS = "no results"
    COUNT_RESULTS = "count results"

    # when agent has recommended
    INFORM = "inform"
    CONTINUE_RECOMMENDATION = "continue_recommendation"

    WELCOME = "welcome"
    RESTART = "restart"
    UNK = "UNK"
    ACKNOWLEDGE = "acknowledge"
    CANT_HELP = "cant help"
    BYE = "bye"

    def __str__(self):
        return self.value
