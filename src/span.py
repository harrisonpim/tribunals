from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

SpanType = Literal["page", "concept", "sentence"]


class Span(BaseModel):
    """A span of text within a document"""

    start_index: int = Field(
        ..., description="The start index of the span within the document text"
    )
    end_index: int = Field(
        ..., description="The end index of the span within the document text"
    )
    identifier: Optional[str] = Field(
        None,
        description="An optional identifier for the span, if it refers to a concept",
    )
    type: Optional[SpanType] = Field(
        None,
        description="An optional type for the span",
    )

    @model_validator(mode="after")
    def validate_indices(self) -> Self:
        """Ensures that the start index is less than the end index"""
        if self.start_index > self.end_index:
            raise ValueError(
                "The start index must be less than the end index "
                f"(got start_index={self.start_index}, end_index={self.end_index})"
            )
        return self

    @model_validator(mode="after")
    def ensure_that_concept_spans_have_identifiers(self) -> Self:
        """Ensures that concept spans have identifiers"""
        if self.type == "concept" and not self.identifier:
            raise ValueError("Concept spans must have identifiers")
        return self
