"""This module contains the ExplainableUserModelTagBased class.

The class generates explanations for user preferences in the movie domain based
on templates loaded from a YAML file.
"""

import random
import re

import yaml
from dialoguekit.core import AnnotatedUtterance
from dialoguekit.participant import DialogueParticipant

from moviebot.explainability.explainable_user_model import (
    ExplainableUserModel,
    UserPreferences,
)

_DEFAULT_TEMPLATE_FILE = "moviebot/explainability/explanation_templates.yaml"


class ExplainableUserModelTagBased(ExplainableUserModel):
    def __init__(self, template_file: str = _DEFAULT_TEMPLATE_FILE):
        """Initialize the ExplainableUserModelTagBased class.

        Args:
            template_file: Path to the YAML file containing explanation
            templates. Defaults to _DEFAULT_TEMPLATE_FILE.
        """
        with open(template_file, "r") as f:
            self.templates = yaml.safe_load(f)

    def generate_explanation(
        self, user_preferences: UserPreferences
    ) -> AnnotatedUtterance:
        """Generate an explanation based on the provided user preferences.

        Args:
            user_preferences: Nested dictionary of user preferences.

        Returns:
            The generated explanation.
        """
        explanation = ""
        for category, prefs in user_preferences.items():
            positive_tags = [tag for tag, value in prefs.items() if value == 1]
            negative_tags = [tag for tag, value in prefs.items() if value == -1]

            for i, tags in enumerate([positive_tags, negative_tags]):
                if len(tags) == 0:
                    continue

                concatenated_tags = ", ".join(tags)
                template = random.choice(self.templates[category]).format(
                    concatenated_tags
                )

                explanation += self._clean_negative_keyword(
                    template, remove=i == 0
                )

        return AnnotatedUtterance(explanation, DialogueParticipant.AGENT)

    def _clean_negative_keyword(
        self, template: str, remove: bool = True
    ) -> str:
        """Removes or keeps negation in template.

        Args:
            template: Template containing negative keyword.
            remove: If True, remove the negative keyword.

        Returns:
            Template with negative keyword removed or replaced.
        """
        if remove:
            return re.sub(r"\[.*?\]", "", template)

        chars_to_remove = "[]"
        trans = str.maketrans("", "", chars_to_remove)
        return template.translate(trans)
