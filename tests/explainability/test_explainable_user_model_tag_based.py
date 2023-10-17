import pytest

from moviebot.explainability.explainable_user_model_tag_based import (
    ExplainableUserModelTagBased,
)


@pytest.fixture
def explainable_model() -> ExplainableUserModelTagBased:
    return ExplainableUserModelTagBased()


def test_generate_explanation_positive(explainable_model):
    user_prefs = {"genres": {"action": 1, "comedy": 1}}
    explanation = explainable_model.generate_explanation(user_prefs)
    assert "action" in explanation.text
    assert "comedy" in explanation.text


def test_generate_explanation_negative(explainable_model):
    user_prefs = {"actors": {"Tom Hanks": -1, "Adam": -1}}
    explanation = explainable_model.generate_explanation(user_prefs)
    assert "Tom Hanks" in explanation.text
    assert "Adam" in explanation.text


def test_generate_explanation_mixed(explainable_model):
    user_prefs = {"keywords": {"war theme": 1, "comic": -1}}
    explanation = explainable_model.generate_explanation(user_prefs)
    assert "war theme" in explanation.text
    assert "comic" in explanation.text


def test_clean_negative_keyword_remove(explainable_model):
    template = "You [don't ]like action."
    cleaned = explainable_model._clean_negative_keyword(template)
    assert cleaned == "You like action."


def test_clean_negative_keyword_keep(explainable_model):
    template = "You [don't ]like action."
    cleaned = explainable_model._clean_negative_keyword(template, remove=False)
    assert cleaned == "You don't like action."
