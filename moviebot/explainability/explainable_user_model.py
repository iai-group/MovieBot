"""Abstract class for creating explainable user models."""

from abc import ABC, abstractmethod
from typing import Dict, List

from dialoguekit.core import AnnotatedUtterance, Annotation

from moviebot.user_modeling.user_model import UserModel

UserPreferences = Dict[str, Dict[str, float]]


class ExplainableUserModel(ABC):
    def __init__(self, user_model: UserModel) -> None:
        self._user_model = user_model

    def get_preferences_as_annotations(self) -> List[Annotation]:
        """Returns the key-value pairs of the user model.

        Returns:
            Key-value pairs of the user model.
        """
        all_preferences = self._user_model.get_all_slot_preferences()
        return [
            Annotation(key, value) for key, value in all_preferences.items()
        ]

    def generate_explanation(self) -> AnnotatedUtterance:
        """Generates an explanation based on the user model.

        Returns:
            A system utterance containing an explanation.
        """
        explanation = self._generate_explanation()
        explanation.annotations = self.get_preferences_as_annotations()
        return explanation

    @abstractmethod
    def _generate_explanation(self) -> AnnotatedUtterance:
        """Generates an explanation based on the provided input data.

        Returns:
            A system utterance containing an explanation.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError(
            "This method must be implemented by a subclass."
        )
