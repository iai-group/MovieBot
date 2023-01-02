"""Ontology is a class that loads ontology files (in .json format) into IAI
MovieBot."""


import json
from typing import Any


class Ontology:
    def __init__(self, path: str) -> None:
        """Initializes the internal structures of the domain.

        Args:
            path: Path to load the ontology from.
        """
        self.ontology_file_path = path
        self.ontology = self.load_ontology()  # ontology as a dictionary
        self.agent_requestable = self.ontology["system_requestable"]
        self.user_requestable = self.ontology["user_requestable"]
        self.slots_not_required_NLU = self.ontology["slots_not_required_NLU"]
        self.slots_annotation = self.ontology["slots_annotation"]
        self.multiple_values_CIN = self.ontology["multiple_values"]

    def load_ontology(self) -> Any:
        """Loads the ontology file.

        Returns:
            Object representing the ontology loaded from JSON file.
        """
        with open(self.ontology_file_path) as ont_file:
            ontology = json.load(ont_file)
        return ontology
