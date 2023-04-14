"""Ontology is a class that loads ontology files (in .json format) into IAI
MovieBot."""


import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Ontology:
    def __init__(self, path: str = None) -> None:
        """Initializes the internal structures of the domain.

        Args:
            path: Path to load the ontology from.
        """
        ontology = self.load_ontology(path)  # ontology as a dictionary
        self.agent_requestable = ontology.get("system_requestable", [])
        self.user_requestable = ontology.get("user_requestable", [])
        self.slots_not_required_NLU = ontology.get("slots_not_required_NLU", [])
        self.slots_annotation = ontology.get("slots_annotation", [])
        self.multiple_values_CIN = ontology.get("multiple_values", [])

    def load_ontology(self, path: str = None) -> Dict[str, Any]:
        """Loads the ontology file.

        Returns:
            Object representing the ontology loaded from JSON file.
        """
        ontology = {}
        if path is not None:
            with open(path) as ont_file:
                ontology = json.load(ont_file)
        else:
            logger.info("No ontology file path provided.")

        return ontology
