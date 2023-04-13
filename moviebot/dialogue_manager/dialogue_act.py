"""Dialogue Act defines the action user or agent takes during the conversation.

The DialogueAct comprises an intent with a list of parameters
(DialogueActItem) for a particular dialogue.
"""


from typing import List, Union

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.nlu.annotation.item_constraint import ItemConstraint


class DialogueAct:
    def __init__(
        self,
        intent: Union[AgentIntents, UserIntents] = None,
        params: List[ItemConstraint] = None,
    ) -> None:
        """Initializes a Dialogue Act.

        Args:
            intent: Intent of the dialogue act. Defaults to None.
            params: Parameters for the particular intent. Defaults to None.
        """
        self.intent = None
        if (
            isinstance(intent, UserIntents) or isinstance(intent, AgentIntents)
        ) and intent is not None:
            self.intent = intent
        else:
            raise ValueError("Unacceptable dialogue act type: %s " % intent)

        self.params = params or []
        assert all(
            isinstance(param, ItemConstraint) for param in self.params
        ), ("All params should be of ItemConstraint type: %s" % params)

    def __str__(self) -> str:
        """Prints a dialogue act to debug the agent.

        Returns:
            String representation of the dialogue act.
        """
        if self.intent:
            params = ", ".join([str(param) for param in self.params])
            return f"{self.intent}({params})"
        else:
            return "None (DialogueAct)"

    def __eq__(self, __o: "DialogueAct") -> bool:
        """Checks if two dialogue acts are equal.

        Args:
            __o: The other dialogue act to compare.

        Returns:
            True if the two dialogue acts are equal.
        """
        return self.intent == __o.intent and self.params == __o.params

    def __hash__(self) -> int:
        """Returns the hash of the dialogue act.

        Returns:
            Hash of the dialogue act.
        """
        return hash((self.intent, tuple(self.params)))

    def remove_constraint(self, constraint: ItemConstraint) -> None:
        """Removes constraint from the list of parameters.

        Args:
            constraint: Constraint to remove.
        """
        while constraint in self.params:
            self.params.remove(constraint)
