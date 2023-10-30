"""Class for creating a tag-based user model explanations.

The class generates explanations for user preferences in the movie domain.
Currently, the explanations are based on movie tags/attributes that were
explicitly mentioned by the user in the conversation.
Future versions of the class will also support implicit tags/attributes, which
are inferred from the movie recommendation feedback. Explanations are based on
the templates loaded from a YAML file.
"""

import os
import random
import re

import yaml

from dialoguekit.core import AnnotatedUtterance
from dialoguekit.participant import DialogueParticipant
from moviebot.explainability.explainable_user_model import (
    ExplainableUserModel,
    UserPreferences,
)

_DEFAULT_TEMPLATE_FILE = "data/explainability/explanation_templates.yaml"


class ExplainableUserModelTagBased(ExplainableUserModel):
    def __init__(self, template_file: str = _DEFAULT_TEMPLATE_FILE):
        """Initializes the ExplainableUserModelTagBased class.

        Args:
            template_file: Path to the YAML file containing explanation
                templates. Defaults to _DEFAULT_TEMPLATE_FILE.

        Raises:
            FileNotFoundError: The template file could not be found.
        """
        if not os.path.isfile(template_file):
            raise FileNotFoundError(
                f"Could not find template file {template_file}."
            )

        with open(template_file, "r") as f:
            self.templates = yaml.safe_load(f)

    def generate_explanation(
        self, user_preferences: UserPreferences
    ) -> AnnotatedUtterance:
        """Generates an explanation based on the provided user preferences.

        Args:
            user_preferences: User preferences.

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
            remove: If True, remove the negative keyword. Defaults to True.

        Returns:
            Template with negative keyword removed or replaced.
        """
        if remove:
            return re.sub(r"\[.*?\]", "", template)

        chars_to_remove = "[]"
        trans = str.maketrans("", "", chars_to_remove)
        return template.translate(trans)
