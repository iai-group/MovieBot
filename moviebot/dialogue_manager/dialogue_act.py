"""Dialogue Act defines the action user or agent takes during the conversation.
"""


from typing import List, Union

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.nlu.annotation.item_constraint import ItemConstraint


class DialogueAct:
    """The DialogueAct comprises of an intent with a list of parameters
    (DialogueActItem) for a particular dialogue."""

    def __init__(
        self,
        intent: Union[AgentIntents, UserIntents] = None,
        params: List[ItemConstraint] = None,
    ) -> None:
        """Initialises a Dialogue Act.

        Args:
            intent: Intent of the dialogue act.
            parmas: Parameters for the particular intent.
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
            string representation of the Dialogue Act

        """
        if self.intent:
            params = ", ".join([str(param) for param in self.params])
            return f"{self.intent}({params})"
        else:
            return "None (DialogueAct)"

    def remove_constraint(self, constraint: ItemConstraint) -> None:
        """Removes constraint from the list of parameters."""
        for p in self.params:
            if p.slot == constraint.slot and p.value == constraint.value:
                self.params.remove(p)
                return
