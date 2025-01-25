from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from src.identifiers import Identifier


class Parent(BaseModel):
    """A parent passage which was used to create the current passage"""

    type: str = Field(..., description="The type of the parent passage")
    id: Identifier = Field(..., description="The ID of the parent passage")
    start_index: int = Field(..., description="The start index of the parent passage")
    end_index: int = Field(..., description="The end index of the parent passage")


class TransformationEvent(BaseModel):
    """An event which describes a transformation of a passage"""

    parents: list[Parent] = Field(
        ...,
        description="The parent passages which were used to create the current passage",
    )
    event_type: str = Field(
        ...,
        description="The function that was called to transform the passage",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="The timestamp of the transformation event",
    )

    @computed_field
    @property
    def id(self) -> Identifier:
        return Identifier.generate(self.parents, self.event_type, self.timestamp)


class Passage(BaseModel):
    """A passage of text within a document"""

    text: str = Field(..., description="The text of the passage")
    document_id: Optional[Identifier] = Field(
        default=None, description="The ID of the document that the passage belongs to"
    )
    transformation_history: list[TransformationEvent] = Field(
        default_factory=list,
        description="The history of transformations applied to the passage",
    )

    @computed_field
    @property
    def id(self) -> Identifier:
        return Identifier.generate(self.document_id, self.text)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @computed_field(repr=False)
    @property
    def zoom_level(self) -> int:
        """
        The number of transformations applied to the passage from the original document.

        A level of 0 indicates that the text is in the raw form extracted from the
        original document, while higher levels indicate increasing levels of abstraction
        from the original text.
        """
        return len(self.transformation_history)

    @property
    def _repr_fields(self) -> dict[str, Any]:
        """
        Fields to include in the passage repr.

        These can be overridden by subclasses
        """
        fields = {
            "id": self.id,
            "zoom_level": self.zoom_level,
        }
        if self.document_id:
            fields["document_id"] = self.document_id
        return fields

    def __repr__(self) -> str:
        repr_contents = ", ".join(
            f"{key}={value}" for key, value in sorted(self._repr_fields.items())
        )
        return f"{self.name}({repr_contents})"

    def __str__(self) -> str:
        return self.__repr__()


class ConceptMention(Passage):
    """A passage of text that refers to a concept"""

    concept_id: Identifier = Field(
        ...,
        description="An identifier for the concept that the mention refers to",
    )

    @property
    def _repr_fields(self) -> dict[str, Any]:
        """Include the concept_id of a ConceptMention in its repr"""
        fields = super()._repr_fields
        fields["concept_id"] = self.concept_id
        return fields


class Page(Passage):
    """A passage of text that represents a page within a document"""

    document_id: Identifier = Field(
        default=..., description="The ID of the document that the page belongs to"
    )
    number: int = Field(
        ...,
        description="The page number of the page within the document",
        ge=1,
    )


class Sentence(Passage):
    """A passage of text that represents a single sentence"""
