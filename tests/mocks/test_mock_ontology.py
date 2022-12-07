from unittest.mock import patch

import moviebot.ontology.ontology as Ont
from tests.mocks.mock_ontology import MockOntology


@patch("moviebot.ontology.ontology.Ontology", new=MockOntology)
def test_mock_data_loader():
    # Setup
    ontology = Ont.Ontology(None)

    # Exercise
    result = ontology.test_method()

    # Results
    truth = 123
    assert result == truth

    # Cleanup - none
