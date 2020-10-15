"""The Dialogue Act Item defines the parameters for a Dialogue Act.
It comprises ot the parameters mentioned in the conversation"""

__author__ = 'Javeria Habib'

from moviebot.dialogue_manager.operator import Operator


class ItemConstraint:
    """The Item Constraint models the parameter of a DialogueAct and is a
    triplet of (slot, operator, value)."""

    def __init__(self, slot, op, value):
        """Initializes a Dialogue Act Item (slot - operator - value)

        Args:
            slot: a string, representing the slot
            op: an Operator
            value: the value of the slot
        """
        if isinstance(slot, str):
            self.slot = slot
        else:
            raise ValueError('Unacceptable slot type: %s ' % slot)

        if op in Operator:
            self.op = op
        else:
            raise ValueError('Unacceptable operator: %s ' % op)

        self.value = value

    def __str__(self):
        """Prints the DAct Item to debug the agent

        Returns:
            string having "<slot> <op> <value>"
        """
        opr = str(self.op)

        result = self.slot

        if self.value:
            result += ' ' + opr + ' ' + str(self.value)

        return result
