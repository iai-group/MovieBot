"""Semantic annotation is annotation that stores certain insight from text. Some
text can have many such annotations."""

from enum import Enum
from typing import Optional

from moviebot.nlu.text_processing import Span


class AnnotationType(Enum):
    """Types of annotations"""

    NAMED_ENTITY = 0
    TEMPORAL = 1
    KEYWORD = 2


class EntityType(Enum):
    """Types of entities. These are subcategories for NAMED_ENTITY annotation
    type."""

    TITLE = 0
    GENRES = 1
    PERSON = 2


class SemanticAnnotation(Span):
    def __init__(
        self,
        annotation_type: AnnotationType,
        entity_type: Optional[EntityType] = None,
        **kwargs,
    ) -> None:
        """Stores annotation type, span and item constraint.

        Span stores information about what section of the text is used in this
        annotation. Item constraint tells us how this annotation is relevant. In
        the case of named entity it holds entity type, and in the case of
        temporal annotation it stores time period or a year.

        Args:
            annotation_type: Type of annotation.
            entity_type: Type of entity. Defaults to None.
            kwargs: Additional span parameters.
        """
        if not isinstance(annotation_type, AnnotationType):
            raise NotImplementedError

        super().__init__(**kwargs)

        self.annotation_type = annotation_type
        self.entity_type = None

        if annotation_type == AnnotationType.NAMED_ENTITY:
            self.entity_type = entity_type

    def get_type(self) -> str:
        """Returns semantic annotation type as string."""
        entity_type_str = (
            f" - {self.entity_type.name}" if self.entity_type else ""
        )
        return (self.annotation_type.name + entity_type_str).lower()

    @classmethod
    def from_span(
        cls,
        span: Span,
        annotation_type: AnnotationType,
        entity_type: Optional[EntityType] = None,
    ) -> "SemanticAnnotation":
        """Creates semantic annotation from already existing span or token. This
        is the most common way to create new annotation.

        Args:
            span: Span with text, start and end.
            annotation_type: Type of annotation.
            entity_type: Type of entity for AnnotationType.NAMED_ENTITY.
              Defaults to None.

        Returns:
            New semantic annotation retaining span information.
        """
        return SemanticAnnotation(
            annotation_type,
            entity_type,
            text=span.text,
            start=span.start,
            end=span.end,
            lemma=span.lemma,
        )
