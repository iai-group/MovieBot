from moviebot.ontology.ontology import Ontology


def test_empty_load_ontology():
    ontology = Ontology()
    assert ontology.agent_requestable == []
    assert ontology.user_requestable == []
    assert ontology.slots_not_required_NLU == []
    assert ontology.slots_annotation == []
    assert ontology.multiple_values_CIN == []


def test_load_ontology():
    ontology = Ontology(path="tests/ontology/ontology.json")
    assert ontology.agent_requestable == ["system_requestable"]
    assert ontology.user_requestable == ["user_requestable"]
    assert ontology.slots_not_required_NLU == ["slots_not_required_NLU"]
    assert ontology.slots_annotation == ["slots_annotation"]
    assert ontology.multiple_values_CIN == ["multiple_values"]
