"""This file contains a class which can be used to annotate slot values in the
user utterance."""

import abc


class SlotAnnotator(abc.ABC):
    """This class can be used to annotate slot values in the user utterance."""

    def __init__(self):
        """Initializes SlotAnnotator.
        """
        pass

    @abc.abstractmethod
    def slot_annotation(self, slot, utterance, raw_utterance):
        """ Given utterance and a slot return a list of triplets of
        (slot, operator, value).

        IMPORTANT: This will be changed to return semantic annotations instead!

        Args:
            slot: Slot for which to annotate utterance
            utterance: Preprocessed utterance to use for annotation

        Returns:
            list(ItemConstraint)
        """
        return None
