"""This file contains a class which can be used to annotate slot values in the
user utterance."""

__author__ = 'Ivica Kostric'

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

        Args:
            slot: Slot for which to annotate utterance
            utterance: Preprocessed utterance to use for annotation
            raw_utterance: Raw utterance

        Returns:
            list(ItemConstraint)
        """
        return None
