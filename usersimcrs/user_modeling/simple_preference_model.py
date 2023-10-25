"""User preference modeling component.

Preferences are stored for (1) items in the collection and (2) slot-value pairs
(for slots defined in the domain).  Preferences are represented as real values
in [-1,1], where zero corresponds to neutral.

This class implements the "single item preference" approach in [Zhang & Balog,
KDD'20].

- Whenever a user is prompted whether they had seen/consumed a specific item, we
  answer that based on historical data.
- Whenever the user is prompted for their preference on a given item or
  slot-value pair, we provide a positive/negative response by flipping a coin
  (i.e., either -1 or +1 as the preference).
- Whenever the user is prompted for a preference on a given slot, a random value
  among the existing slot values is picked and returned as positive preference.

The responses given are remembered so that the user would respond the same way
if they are asked the same question again.

This approach offers limited consistency. Items that are seen/consumed are
rooted in real user behavior, but the preferences expressed about them are not.
Hence, the user might express a preference about a slot that is inconsistent
with the answers given to other questions (e.g., likes "action" as a genre, but
has not seen a single action movie).
"""

import random
from typing import Tuple

from dialoguekit.core.domain import Domain
from dialoguekit.participant.user_preferences import UserPreferences

from usersimcrs.items.item_collection import ItemCollection
from usersimcrs.items.ratings import Ratings
from usersimcrs.user_modeling.preference_model import (
    KEY_ITEM_ID,
    PreferenceModel,
)


class SimplePreferenceModel(PreferenceModel):
    """Representation of the user's preferences."""

    # Above this threshold, a preference is considered positive;
    # below -1 x this threshold, a preference is considered negative;
    # otherwise, it's considered neutral.
    PREFERENCE_THRESHOLD = 0.25

    def __init__(
        self,
        domain: Domain,
        item_collection: ItemCollection,
        historical_ratings: Ratings,
        historical_user_id: str = None,
    ) -> None:
        """Generates a simulated user, by assigning initial preferences based
        on historical ratings according to the specified model type (SIP or
        PKG).

        Further preferences are inferred along the way as the simulated user is
        being prompted by the agent for preferences.

        Args:
            domain: Domain.
            item_collection: Item collection.
            historical_ratings: Historical ratings.
            historical_user_id (Optional): If provided, the simulated user is
                based on this particular historical user; otherwise, it is based
                on a randomly sampled user. This is mostly added to make the
                class testable.
        """
        super().__init__(
            domain, item_collection, historical_ratings, historical_user_id
        )

        # Store item and slot-value preferences separately.
        self._item_preferences = UserPreferences(self._user_id)
        self._slot_value_preferences = UserPreferences(self._user_id)

    def get_item_preference(self, item_id: str) -> float:
        """Returns a preference for a given item.

        This is used to answer questions like: "How did you like it?",
        where "it" refers to the movie mentioned previously.

        Args:
            item_id: Item ID.

        Returns:
            Randomly chosen preference, which is generally in [-1,1], but in
            case of the simple preference model it's either -1 or +1.

        Raises:
            ValueError: If the item does not exist in the collection.
        """
        self._assert_item_exists(item_id)
        preference = self._item_preferences.get_preference(KEY_ITEM_ID, item_id)
        if not preference:
            preference = random.choice([-1, 1])
            self._item_preferences.set_preference(
                KEY_ITEM_ID, item_id, preference
            )
        return preference

    def get_slot_value_preference(self, slot: str, value: str) -> float:
        """Returns a preference on a given slot-value pair.

        This is used to answer questions like: "Do you like action movies?"

        Args:
            slot: Slot name (needs to exist in the domain).
            value: Slot value.

        Returns:
            Randomly chosen preference, which is either -1 or +1.
        """
        self._assert_slot_exists(slot)
        preference = self._slot_value_preferences.get_preference(slot, value)
        if not preference:
            preference = random.choice([-1, 1])
            self._slot_value_preferences.set_preference(slot, value, preference)
        return preference

    def get_slot_preference(self, slot: str) -> Tuple[str, float]:
        """Returns a preferred value for a given slot.

        This is used to answer questions like: "What movie genre do you prefer?"

        While in principle negative preferences could also be returned, here it
        is always a positive preference that is expressed.

        Args:
            slot: Slot name (needs to exist in the domain).

        Returns:
            A value and corresponding preferences; if no preference could be
            obtained for that slot, then (None, 0) are returned.
        """
        self._assert_slot_exists(slot)
        preference = None
        attempts = 0

        while not preference:
            # Pick a random value for the slot.
            value: str = random.choice(
                list(self._item_collection.get_possible_property_values(slot))
            )
            # If there is either (1) a positive preference on that value from
            # before, or (2) there is no preference, then it can be returned.
            # Otherwise, we try again to sample a different value for the slot.
            preference = self._slot_value_preferences.get_preference(
                slot, value
            )
            if preference is None:
                preference = 1
                self._slot_value_preferences.set_preference(
                    slot, value, preference
                )
            # There is preference from before, but not positive; need to find a
            # different value.
            elif preference != 1:
                preference = None

            # It would in principle be possible to enter into an infinite loop
            # here (e.g., if there is a small set of possible values for the
            # slot and the user has already expressed negative preference on all
            # of them), therefore we limit the number of attempts.
            attempts += 1
            if attempts == 10:
                return None, 0

        return value, preference
