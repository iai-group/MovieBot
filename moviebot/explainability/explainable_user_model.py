"""Abstract class for creating explainable user models."""

from abc import ABC, abstractmethod
from typing import Dict

from dialoguekit.core import AnnotatedUtterance

UserPreferences = Dict[str, Dict[str, float]]


class ExplainableUserModel(ABC):
    @abstractmethod
    def generate_explanation(
        self, user_preferences: UserPreferences
    ) -> AnnotatedUtterance:
        """Generates an explanation based on the provided input data.

        Args:
            input_data: The input data for which an explanation is to be
            generated.

        Returns:
            A system utterance containing an explanation.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError(
            "This method must be implemented by a subclass."
        )
