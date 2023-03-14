"""Recommender model based on slot value pairs."""

from typing import Any, Dict, List

from moviebot.database.database import DataBase
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.ontology.ontology import Ontology
from moviebot.recommender.recommender_model import RecommenderModel


class SlotBasedRecommenderModel(RecommenderModel):
    def __init__(self, db: DataBase, ontology: Ontology) -> None:
        """Instantiates a slot-based recommender model.

        Args:
            db: Database with available items.
            ontology: Ontology.
        """
        super().__init__(db, ontology)

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
