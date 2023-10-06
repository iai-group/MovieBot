"""This module is used to process the user's decision on a movie recommendation.
"""

from enum import Enum


class RecommendationChoices(Enum):
    """Enum class for recommendation choices."""

    ACCEPT = "accept"
    REJECT = "reject"
    DONT_LIKE = "dont_like"
    WATCHED = "watched"


def convert_choice_to_preference(choice: RecommendationChoices) -> float:
    """Converts a choice to a preference within the range [-1,1].

    Dislike is represented by a preference below 0, while like is
    represented by a preference above 0. If the choice does not express a
    preference (e.g., inquire), then the preference is neutral, i.e., 0.
    Possible choices are: accept, reject, dont_like, inquire, and watched.

    Args:
        choice: Choice.

    Returns:
        Preference within the range [-1,1].
    """
    if choice == RecommendationChoices.ACCEPT:
        return 1.0
    elif choice in [
        RecommendationChoices.REJECT,
        RecommendationChoices.DONT_LIKE,
    ]:
        return -1.0

    return 0.0
