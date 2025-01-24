import json
from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field, computed_field

from src.identifiers import Identifier


class Concept(BaseModel):
    """A concept with a preferred label and optional description"""

    preferred_label: str = Field(..., description="The preferred label for the concept")
    description: str = Field(
        default="",
        description=(
            "An optional description of the concept with enough detail to disambiguate "
            "it from similar concepts"
        ),
    )
    alternative_labels: list[str] = Field(
        default_factory=list, description="A list of alternative labels for the concept"
    )
    examples: list[str] = Field(
        default_factory=list, description="A list of examples of the concept"
    )

    @computed_field
    @property
    def all_labels(self) -> list[str]:
        return [self.preferred_label] + self.alternative_labels

    def __repr__(self) -> str:
        return f"Concept({self.preferred_label})"

    def __str__(self) -> str:
        return self.__repr__()

    @computed_field
    @property
    def id(self) -> Identifier:
        return Identifier.generate(self.all_labels)

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> "Concept":
        with open(file_path) as f:
            data = json.load(f)
        return cls(**data)

    def save(self, file_path: Union[str, Path]) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
