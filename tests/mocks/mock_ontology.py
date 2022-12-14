ontology = {
    "slots_annotation": [
        "actors",
        "directors",
    ],
}


class MockOntology:
    def __init__(self, path):
        pass

    def load_ontolgy(self):
        return ontology

    def test_method(self):
        return 123
