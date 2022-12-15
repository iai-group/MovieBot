ontology = {
    "slots_annotation": [
        "actors",
        "directors",
    ],
}


class MockOntology:
    def __init__(self, path: str = None):
        self.ontology = self.load_ontology()
        self.slots_annotation = self.ontology["slots_annotation"]

    def load_ontology(self):
        return ontology

    def test_method(self):
        return 123
