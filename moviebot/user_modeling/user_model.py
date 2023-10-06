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

_KEY_SLOT_PREFERENCES = "slot_preferences"
_KEY_SLOT_PREFERENCES_NL = "slot_preferences_nl"
_KEY_ITEM_PREFERENCES = "item_preferences"
_KEY_ITEM_PREFERENCES_NL = "item_preferences_nl"


class UserModel:
    def __init__(self) -> None:
        """Initializes the user model."""
        # Structured and unstructured slot preferences
        self.slot_preferences: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.slot_preferences_nl: Dict[
            str, Dict[str, AnnotatedUtterance]
        ] = defaultdict(lambda: defaultdict(list))

        # Structured and unstructured item preferences
        self.item_preferences: Dict[str, float] = defaultdict(float)

        self.item_preferences_nl: Dict[
            str, List[AnnotatedUtterance]
        ] = defaultdict(list)

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
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file {json_path} not found.")

        user_model_json = json.load(open(json_path, "r"))
        user_model.slot_preferences.update(
            user_model_json[_KEY_SLOT_PREFERENCES]
        )
        for slot, utterance in user_model_json[
            _KEY_SLOT_PREFERENCES_NL
        ].items():
            user_model.slot_preferences_nl[slot].append(
                json_to_annotated_utterance(utterance)
            )

        user_model.item_preferences.update(
            user_model_json[_KEY_ITEM_PREFERENCES]
        )
        for item, utterance in user_model_json[
            _KEY_ITEM_PREFERENCES_NL
        ].items():
            user_model.item_preferences_nl[item].append(
                json_to_annotated_utterance(utterance)
            )
        return user_model

    def _utterance_to_dict(
        self, utterance: AnnotatedUtterance
    ) -> Dict[str, str]:
        """Converts an utterance to a dictionary.

        TODO: Move this method to DialogueKit AnnotatedUtterance class.
        See: https://github.com/iai-group/DialogueKit/issues/248

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

    def save_as_json_file(self, json_path: str) -> None:
        """Saves the user model to a JSON file.

        Args:
            json_path: Path to the JSON file.
        """
        data = {
            _KEY_SLOT_PREFERENCES: self.slot_preferences,
            _KEY_ITEM_PREFERENCES: self.item_preferences,
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
                _KEY_SLOT_PREFERENCES_NL: slot_preferences_utterances,
                _KEY_ITEM_PREFERENCES_NL: item_preferences_utterances,
            }
        )
        json.dump(data, open(json_path, "w"), indent=4)

    def update_item_preference(self, item: str, preference: float) -> None:
        """Updates the preference for a given item.

        Args:
            item: Item.
            preference: Preference.
        """
        self.item_preferences[item] = preference

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
    ) -> Dict[str, float]:
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
