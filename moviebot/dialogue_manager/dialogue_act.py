"""Dialogue Act defines the action user or agent takes during the conversation.

The DialogueAct comprises of an intent with a list of parameters
(DialogueActItem) for a particular dialogue.
"""


from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents


class DialogueAct:
    def __init__(self, intent=None, params=None) -> None:
        """Initializes a Dialogue Act.

        Args:
            intent: Intent of the dialogue act.
            params: Parameters for the particular intent.
        """
        self.intent = None
        if (
            isinstance(intent, UserIntents) or isinstance(intent, AgentIntents)
        ) and intent is not None:
            self.intent = intent
        else:
            raise ValueError("Unacceptable dialogue act type: %s " % intent)

        self.params = params or []

    def __str__(self) -> str:
        """Prints a dialogue act to debug the agent.

        Returns:
            String representation of the DialogueAct.
        """
        if self.intent:
            params = ", ".join([str(param) for param in self.params])
            return f"{self.intent}({params})"
        else:
            return "None (DialogueAct)"
