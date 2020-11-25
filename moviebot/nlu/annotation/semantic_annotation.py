"""Semantic annotation is annotation that stores certain insight from text. Some
text can have many such annotatins. """

from typing import Text, Optional
from enum import Enum

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
    ACTORS = 2
    DIRECTORS = 3


class SemanticAnnotation(Span):
    """Stores annotation type, span and item constraint. Span stores
    information about what section of the text is used in this annotation.
    Item constraint tells us how this annotation is relevant. In the case of
    named entity it holds entity type, and in the case of temporal annotation
    stores time period or a year.

    """

    def __init__(
        self,
        annotation_type: AnnotationType,
        entity_type: Optional[EntityType] = None,
        **kwargs,
    ) -> None:

        if not isinstance(annotation_type, AnnotationType):
            raise NotImplementedError

        super().__init__(**kwargs)

        self.annotation_type = annotation_type
        self.entity_type = None

        if annotation_type == AnnotationType.NAMED_ENTITY:
            self.entity_type = entity_type

    def get_type(self) -> Text:
        entity_type = ' - ' + self.entity_type.name if self.entity_type else ''
        return (self.annotation_type.name + entity_type).lower()

    @classmethod
    def from_span(
        cls,
        span: Span,
        annotation_type: AnnotationType,
        entity_type: Optional[EntityType] = None,
    ):
        """Create semantic annotation from already existing span or token. This
        is the most common way to create new annotation.

        Args:
            span (Span): span with text, start and end
            annotation_type (AnnotationType): Type of annotation
            entity_type (Optional[EntityType], optional): Type of entity for
                AnnotationType.NAMED_ENTITY. Defaults to None.

        Returns:
            [type]: [description]
        """
        return SemanticAnnotation(annotation_type,
                                  entity_type,
                                  text=span.text,
                                  start=span.start,
                                  end=span.end,
                                  lemma=span.lemma)
