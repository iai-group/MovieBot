"""Class for user modeling.

The user model stores the user's preferences, in terms of slots and items in a
structured (dictionary) and unstructured manner (utterances). These preferences
serve two main purposes:
1. Input for the recommender system.
2. Input for the explainability component to generate an explainable user model.
"""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from typing import Dict, List, Optional, Union

from dialoguekit.core import AnnotatedUtterance
from dialoguekit.utils.dialogue_reader import json_to_annotated_utterance


class UserModel:
    def __init__(self) -> None:
        """Initializes the user model."""
        # Structured and unstructured slot preferences
        self.slot_preferences: Dict[Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.slot_preferences_nl: Dict[
            Dict[str, AnnotatedUtterance]
        ] = defaultdict(lambda: defaultdict(list))

        # Structured and unstructured item preferences
        self.item_preferences: Dict[Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.item_preferences_nl: Dict[
            Dict[str, AnnotatedUtterance]
        ] = defaultdict(lambda: defaultdict(list))

    @classmethod
    def from_json(cls, json_path: str) -> UserModel:
        """Loads a user model from a JSON file.

        Args:
            json_path: Path to the JSON file.

        Raises:
            FileNotFoundError: If the JSON file is not found.

        Returns:
            User model.
        """
        user_model = cls()
        if os.path.exists(json_path):
            user_model_json = json.load(open(json_path, "r"))
            user_model.slot_preferences.update(
                user_model_json["slot_preferences"]
            )
            for slot, utterance in user_model_json[
                "slot_preferences_nl"
            ].items():
                user_model.slot_preferences_nl[slot].append(
                    json_to_annotated_utterance(utterance)
                )

            user_model.item_preferences.update(
                user_model_json["item_preferences"]
            )
            for item, utterance in user_model_json[
                "item_preferences_nl"
            ].items():
                user_model.item_preferences_nl[item].append(
                    json_to_annotated_utterance(utterance)
                )
        else:
            raise FileNotFoundError(f"JSON file {json_path} not found.")
        return user_model

    def _utterance_to_dict(
        self, utterance: AnnotatedUtterance
    ) -> Dict[str, str]:
        """Converts an utterance to a dictionary.

        TODO: Move this method to DialogueKit AnnotatedUtterance class.

        Args:
            utterance: Utterance.

        Returns:
            Dictionary with utterance information.
        """
        return {
            "participant": utterance.participant.name,
            "utterance": utterance.text,
            "intent": utterance.intent.label,
            "slot_values": [
                [annotation.slot, annotation.value]
                for annotation in utterance.annotations
            ]
            if utterance.annotations
            else [],
        }

    def save(self, json_path: str) -> None:
        """Saves the user model to a JSON file.

        Args:
            json_path: Path to the JSON file.
        """
        data = {
            "slot_preferences": self.slot_preferences,
            "item_preferences": self.item_preferences,
        }

        slot_preferences_utterances = {}
        for slot, utterances in self.slot_preferences_nl.items():
            slot_preferences_utterances[slot] = [
                self._utterance_to_dict(utterance) for utterance in utterances
            ]

        item_preferences_utterances = {}
        for item, utterances in self.item_preferences_nl.items():
            item_preferences_utterances[item] = [
                self._utterance_to_dict(utterance) for utterance in utterances
            ]

        data.update(
            {
                "slot_preferences_nl": slot_preferences_utterances,
                "item_preferences_nl": item_preferences_utterances,
            }
        )
        json.dump(data, open(json_path, "w"), indent=4)

    def _convert_choice_to_preference(self, choice: str) -> float:
        """Converts a choice to a preference within the range [-1,1].

        Dislike is represented by a preference below 0, while like is
        represented by a preference above 0. If the choice does not express a
        preference (i.e., inquire), then the preference is neutral, i.e., 0.
        Possible choices are: accept, reject, dont_like, inquire, and watched.

        Args:
            choice: Choice (i.e., accept, reject).

        Returns:
            Preference within the range [-1,1].
        """
        if choice == "accept":
            return 1.0
        elif choice in ["reject", "dont_like"]:
            return -1.0

        return 0.0

    def update_item_preference(self, item: str, choice: str) -> None:
        """Updates the preference for a given item.

        Args:
            item: Item.
            choice: Choice (i.e., accept, reject, don't like).
        """
        self.item_preferences[item][
            choice
        ] = self._convert_choice_to_preference(choice)

    def get_utterances_with_item_preferences(
        self, item: Optional[str] = None
    ) -> List[AnnotatedUtterance]:
        """Returns the utterances with item preference.

        If no item is provided, then all the utterances with item preference
        are returned. Else, only the utterances with item preference for the
        given item are returned.

        Args:
            item: Item. Defaults to None.

        Returns:
            Utterances with item preference.
        """
        if item is None:
            return [
                utterance
                for utterances in self.item_preferences_nl.values()
                for utterance in utterances
            ]

        if item not in self.item_preferences_nl:
            logging.warning(f"Item {item} not found in user model.")
        return self.item_preferences_nl.get(item, [])

    def get_item_preferences(
        self, item: Optional[str] = None
    ) -> Union[Dict[str, float], float]:
        """Returns the item preferences.

        If no item is provided, then all the item preferences are returned.
        Else, only the item preferences for the given item are returned.

        Args:
            item: Item. Defaults to None.

        Returns:
            Item preferences.
        """
        if item is None:
            return self.item_preferences

        if item not in self.item_preferences:
            logging.warning(f"Item {item} not found in user model.")
        return self.item_preferences.get(item, None)

    def get_utterances_with_slot_preferences(
        self, slot: Optional[str] = None
    ) -> List[AnnotatedUtterance]:
        """Returns the utterances with slot preference.

        If no slot is provided, then all the utterances with slot preference
        are returned. Else, only the utterances with slot preference for the
        given slot are returned.

        Args:
            slot: Slot. Defaults to None.

        Returns:
            Utterances with slot preference.
        """
        if slot is None:
            return [
                utterance
                for utterances in self.slot_preferences_nl.values()
                for utterance in utterances
            ]

        if slot not in self.slot_preferences_nl:
            logging.warning(f"Slot {slot} not found in user model.")
        return self.slot_preferences_nl.get(slot, [])

    def get_slot_preferences(
        self, slot: Optional[str] = None
    ) -> Union[Dict[str, float], float]:
        """Returns the slot preferences.

        If no slot is provided, then all the slot preferences are returned.
        Else, only the slot preferences for the given slot are returned.

        Args:
            slot: Slot. Defaults to None.

        Returns:
            Slot preferences.
        """
        if slot is None:
            return self.slot_preferences

        if slot not in self.slot_preferences:
            logging.warning(f"Slot {slot} not found in user model.")
        return self.slot_preferences.get(slot, None)
