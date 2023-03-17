"""Recommender model based on slot value pairs."""

from typing import Any, Dict, List

from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.recommender.recommender_model import RecommenderModel


class SlotBasedRecommenderModel(RecommenderModel):
    def recommend_items(
        self, dialogue_state: DialogueState
    ) -> List[Dict[str, Any]]:
        """Recommends movies based on slot-value pairs.

        Args:
            dialogue_state: Dialogue state.

        Returns:
            Recommended movies.
        """
        database_result = self._db.database_lookup(
            dialogue_state, self._ontology
        )
        return database_result
