from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from src.identifiers import Identifier


class Passage(BaseModel):
    """A passage of text within a document"""

    text: str = Field(..., description="The text of the passage")
    start_index: int = Field(
        ...,
        description="The start index of the passage within the document",
        ge=0,
    )
    end_index: int = Field(
        ...,
        description="The end index of the passage within the document",
        ge=0,
    )
    document_id: Optional[Identifier] = Field(
        default=None, description="The ID of the document that the passage belongs to"
    )
    zoom_level: int = Field(
        default=0,
        description=(
            "A numeric representation of the level of abstraction away from the "
            "original raw text. "
            "0 should always represent raw text, 1 might represent a detailed summary, "
            "2 might represent key concepts/topics, and 3+ might represent higher "
            "levels of abstraction"
        ),
    )

    @computed_field
    @property
    def id(self) -> Identifier:
        return Identifier.generate(
            self.document_id, self.text, self.start_index, self.end_index
        )

    @property
    def name(self) -> str:
        return self.__class__.__name__

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
