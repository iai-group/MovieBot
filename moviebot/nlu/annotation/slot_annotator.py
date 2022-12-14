"""This file contains a class which can be used to annotate slot values in the
user utterance."""

import abc
from typing import List

from moviebot.core.utterance.utterance import UserUtterance
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.slots import Slots


class SlotAnnotator(abc.ABC):
    """This class is used to annotate slot values in the user utterance."""

    @abc.abstractmethod
    def slot_annotation(
        self, slot: Slots, utterance: UserUtterance
    ) -> List[ItemConstraint]:
        """Given utterance and a slot return a list of triplets of
        (slot, operator, value).

        IMPORTANT: This will be changed to return semantic annotations instead!

        Args:
            slot (Slots): Slot for which to annotate
            utterance (UserUtterance): User utterance class which contains both
                original utterance and utterance tokens.

        Raises:
            NotImplementedError: Must be overridden

        Returns:
            List[ItemConstraint]: List of constraints
        """
        raise NotImplementedError
