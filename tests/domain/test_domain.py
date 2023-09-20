"""Tests for MovieDomain class."""

from moviebot.domain.movie_domain import MovieDomain


def test_init() -> None:
    """Tests initialization of MovieDomain class."""
    domain = MovieDomain("tests/data/test_domain.yaml")

    assert domain.agent_requestable == ["genres", "keywords"]
    assert domain.user_requestable == [
        "genres",
        "duration",
        "actors",
        "directors",
        "year",
    ]
    assert domain.slots_not_required_NLU == []
    assert domain.slots_annotation == ["actors", "directors"]
    assert domain.multiple_values_CIN == ["genres"]
    assert len(domain.get_slot_names()) == 6
