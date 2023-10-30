"""User preference modeling component based on PKG."""

import random
from typing import Tuple

from dialoguekit.core.domain import Domain

from usersimcrs.items.item_collection import ItemCollection
from usersimcrs.items.ratings import Ratings
from usersimcrs.user_modeling.preference_model import PreferenceModel


class PKGPreferenceModel(PreferenceModel):
    """Representation of the user's preferences with a PKG."""

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
        # TODO Open connection to PKG

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
        # TODO
        preference = None
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
        # TODO
        preference = None
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
            # TODO

            # There is preference from before, but not positive; need to find a
            # different value.
            # TODO

            # It would in principle be possible to enter into an infinite loop
            # here (e.g., if there is a small set of possible values for the
            # slot and the user has already expressed negative preference on all
            # of them), therefore we limit the number of attempts.
            attempts += 1
            if attempts == 10:
                return None, 0

        return value, preference
