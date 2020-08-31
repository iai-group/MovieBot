"""Ontology is a class that loads ontology files (in .json format) into IAI MovieBot."""

__author__ = "Javeria Habib"

import json


class Ontology:
    """Ontology is a class that loads ontology files (in .json format) into IAI MovieBot."""

    def __init__(self, path):
        """Initializes the internal structures of the Domain

        :param path: path to load the ontology from
        """
        self.ontology_file_path = path
        self.ontology = self.load_ontology()  # ontology as a dictionary
        self.agent_requestable = self.ontology["system_requestable"]
        self.user_requestable = self.ontology["user_requestable"]
        self.slots_not_required_NLU = self.ontology["slots_not_required_NLU"]
        self.slots_annotation = self.ontology['slots_annotation']
        self.multiple_values_CIN = self.ontology["multiple_values"]

    def load_ontology(self):
        """Loads the ontology file

        :return: nothing
        """
        with open(self.ontology_file_path) as ont_file:
            ontology = json.load(ont_file)
        return ontology
