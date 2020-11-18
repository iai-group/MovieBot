"""The Dialogue Act Item defines the parameters for a Dialogue Act.
It comprises ot the parameters mentioned in the conversation"""

__author__ = 'Javeria Habib'

from typing import Optional, List, Text, Any
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.semantic_annotation import SemanticAnnotation


class ItemConstraint:
    """The Item Constraint models the parameter of a DialogueAct and is a
    triplet of (slot, operator, value)."""

    def __init__(self,
                 slot: Text,
                 op: Operator,
                 value: Any,
                 annotation: Optional[SemanticAnnotation] = None) -> None:
        """Initializes a Dialogue Act Item (slot - operator - value)

        Args:
            slot (Text): a string, representing the slot
            op (Operator): an Operator
            value (Any): the value of the slot
            annotation (Optional[SemanticAnnotation], optional): Semantic
                annotation if the constraint is due to annotation. Defaults to
                None.

        Raises:
            ValueError: slot should be string
            ValueError: op should be Operator class
        """
        if not isinstance(slot, str):
            raise ValueError('Unacceptable slot type: %s ' % slot)

        if op not in Operator:
            raise ValueError('Unacceptable operator: %s ' % op)

        self.op = op
        self.slot = slot
        self.value = value
        self.annotation = [annotation] if annotation else []

    def add_value(self,
                  value: Any,
                  annotation: Optional[SemanticAnnotation] = None) -> None:
        """Adds value

        Args:
            value (Any): value to add
            annotation (Optional[SemanticAnnotation], optional): Semantic
                annotation if adding value is due to annotation. Defaults to
                None.
        """
        self.value += ' ' + str(value)
        if annotation:
            self.annotation.append(annotation)

    def __eq__(self, other) -> bool:
        return (self.slot, self.op, self.value) == (other.slot, other.op,
                                                    other.value)

    def __str__(self) -> Text:
        """Prints the DAct Item to debug the agent

        Returns:
            string having "<slot> <op> <value>"
        """
        opr = str(self.op)

        result = self.slot

        if self.value:
            result += ' ' + opr + ' ' + str(self.value)

        return result
