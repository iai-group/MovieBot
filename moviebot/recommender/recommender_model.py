"""Interface for recommender model."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from moviebot.database.db_movies import DataBase
from moviebot.dialogue_manager.dialogue_state import DialogueState


class RecommenderModel(ABC):
    def __init__(self, db: DataBase) -> None:
        """Instantiates a recommender model.

        Args:
            db: Database with available items.
        """
        super().__init__()
        self._db = db

    @abstractmethod
    def recommend_items(
        self, dialogue_state: DialogueState
    ) -> List[Dict[str, Any]]:
        """Recommends movies.

        Args:
            dialogue_state: Dialogue state.

        Returns:
            Recommended movies.

        Raises:
            NotImplementedError: If not implemented in derived class.
        """
        raise NotImplementedError

    def get_previous_recommend_items(self) -> List[Dict[str, Any]]:
        """Retrieves the previous recommendations.

        Returns:
            List of previously recommended movies.
        """
        return self._db.backup_db_results
