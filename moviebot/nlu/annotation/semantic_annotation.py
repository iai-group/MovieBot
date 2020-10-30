"""Semantic annotation is annotation that stores certain insight from text. Some
text can have many such annotatins. """

from typing import Text
from enum import Enum

from moviebot.nlu.text_processing import Token
from moviebot.nlu.annotation.item_constraint import ItemConstraint


class AnnotationType(Enum):
    """Types of annotations"""

    NAMED_ENTITY = 'named_entity'
    TEMPORAL = 'temporal'
    KEYWORD = 'keyword'


class EntityType(Enum):
    """Types of entities. These are subcategories for NAMED_ENTITY annotation
    type."""

    TITLE = 'title'
    GENRE = 'genre'
    ACTOR = 'actor'
    DIRECTOR = 'director'


class SemanticAnnotation:
    """Stores annotation type, token and item constraint. Token stores
    information about what section of the text is used in this annotation.
    Item constraint tells us how this annotation is relevant. In the case of
    named entity it holds entity type, and in the case of temporal annotation
    stores time period or a year.

    """

    def __init__(self, annotation_type: AnnotationType, token: Token,
                 item_constraint: ItemConstraint) -> None:

        if not isinstance(annotation_type, AnnotationType):
            raise NotImplementedError

        if not isinstance(token, Token):
            raise NotImplementedError

        if not isinstance(item_constraint, ItemConstraint):
            raise NotImplementedError

        self.annotation_type = annotation_type
        self.token = token
        self.item_constraint = item_constraint

    def get_type(self) -> Text:
        if self.annotation_type == AnnotationType.NAMED_ENTITY:
            return f'{self.annotation_type.name} - {self.item_constraint.slot}'
        return self.annotation_type.name
