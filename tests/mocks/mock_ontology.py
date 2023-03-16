ontology = {
    "slots_annotation": [
        "actors",
        "directors",
    ],
    "system_requestable": ["genres", "keywords"],
    "user_requestable": [
        "genres",
        "duration",
        "actors",
        "directors",
        "year",
    ],
    "multiple_values": ["genres"],
}


class MockOntology:
    def __init__(self, path: str = None):
        self.ontology = self.load_ontology()
        self.slots_annotation = self.ontology["slots_annotation"]
        self.agent_requestable = self.ontology["system_requestable"]
        self.user_requestable = self.ontology["user_requestable"]
        self.multiple_values_CIN = self.ontology["multiple_values"]

    def load_ontology(self):
        return ontology

    def test_method(self):
        return 123
