"""Test for ItemConstraint class."""
import pytest

from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.semantic_annotation import (
    AnnotationType,
    EntityType,
    SemanticAnnotation,
)
from moviebot.nlu.text_processing import Span


@pytest.fixture
def item_constraint() -> ItemConstraint:
    with pytest.raises(ValueError):
        ItemConstraint(1, Operator.AND, "value")
    with pytest.raises(ValueError):
        ItemConstraint("genre", Operator(0), "comedy")

    ic = ItemConstraint("genre", Operator.AND, "comedy")
    return ic


def test_add_value(item_constraint: ItemConstraint) -> None:
    additional_value = "dramatic"
    annotation = SemanticAnnotation.from_span(
        Span("comedy dramatic", 0),
        AnnotationType.NAMED_ENTITY,
        EntityType.GENRES,
    )
    item_constraint.add_value(additional_value, annotation=annotation)

    assert item_constraint.value == f"comedy {additional_value}"
    assert len(item_constraint.annotation) == 1


def test___str__(item_constraint: ItemConstraint) -> None:
    representation = "genre AND comedy"
    assert item_constraint.__str__() == representation
