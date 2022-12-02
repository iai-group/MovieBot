"""Dialogue Act defines the action user or agent takes during the conversation.
"""


from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents


class DialogueAct:
    """The DialogueAct comprises of an intent with a list of parameters
    (DialogueActItem) for a particular dialogue."""

    def __init__(self, intent=None, params=None):
        """Initialises a Dialogue Act.

        Args:
            intent: intent of the DAct
            parmas: parameters for the particular intent.

        """
        self.intent = None
        if (
            isinstance(intent, UserIntents) or isinstance(intent, AgentIntents)
        ) and intent is not None:
            self.intent = intent
        else:
            raise ValueError("Unacceptable dialogue act type: %s " % intent)

        self.params = params or []

    def __str__(self):
        """Prints a dialogue act to debug the agent.

        Returns:
            string representation of the Dialogue Act

        """
        if self.intent:
            return (
                str(self.intent)
                + "("
                + ", ".join([str(param) for param in self.params])
                + ")"
            )
        else:
            return "None (DialogueAct)"
