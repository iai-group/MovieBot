"""The Dialogue Act Item defines the parameters for a Dialogue Act.

It comprises ot the parameters mentioned in the conversation.
"""


from typing import Any, Optional

from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.semantic_annotation import SemanticAnnotation


class ItemConstraint:
    def __init__(
        self,
        slot: str,
        op: Operator,
        value: Any,
        annotation: Optional[SemanticAnnotation] = None,
    ) -> None:
        """The Item Constraint models the parameter of a DialogueAct and is a
        triplet of (slot, operator, value).

        Args:
            slot: A string representing the slot.
            op: An Operator.
            value: The value of the slot.
            annotation: Semantic annotation if the constraint is due to
              annotation. Defaults to None.

        Raises:
            ValueError: slot should be string.
            ValueError: op should be Operator class.
        """
        if not isinstance(slot, str):
            raise ValueError("Unacceptable slot type: %s " % slot)

        if op not in Operator:
            raise ValueError("Unacceptable operator: %s " % op)

        self.op = op
        self.slot = slot
        self.value = value
        self.annotation = [annotation] if annotation else []

    def add_value(
        self, value: Any, annotation: Optional[SemanticAnnotation] = None
    ) -> None:
        """Adds value and annotation if any.

        Args:
            value: Value to add.
            annotation: Semantic annotation if adding value is due to
              annotation. Defaults to None.
        """
        self.value += f" {str(value)}"
        if annotation:
            self.annotation.append(annotation)

    def __eq__(self, other) -> bool:
        return (self.slot, self.op, self.value) == (
            other.slot,
            other.op,
            other.value,
        )

    def __hash__(self) -> int:
        return hash((self.slot, self.op, self.value))

    def __str__(self) -> str:
        """Prints the DAct Item to debug the agent.

        Returns:
            String having "<slot> <op> <value>".
        """
        opr = str(self.op)

        result = self.slot

        if self.value:
            result += f" {opr} {self.value}"

        return result
