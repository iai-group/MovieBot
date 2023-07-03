"""This file contains the list of possible intents for agent/system as
constants. This approach will help the Dialogue Policy to decide the intents
from a pre-defined set."""


from enum import Enum

from dialoguekit.core import Intent


class AgentIntents(Enum):
    """This class contains the list of possible intents for agent/system as
    constants. This approach will help the Dialogue Policy to decide the intents
    from a pre-defined set."""

    ELICIT = Intent("elicit")

    # When agent has results
    RECOMMEND = Intent("recommend")
    NO_RESULTS = Intent("no results")
    COUNT_RESULTS = Intent("count results")

    # when agent has recommended
    INFORM = Intent("inform")
    CONTINUE_RECOMMENDATION = Intent("continue_recommendation")

    WELCOME = Intent("welcome")
    RESTART = Intent("restart")
    UNK = Intent("UNK")
    ACKNOWLEDGE = Intent("acknowledge")
    CANT_HELP = Intent("cant help")
    BYE = Intent("bye")
