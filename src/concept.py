import json
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, Field, computed_field

from src.identifiers import pretty_hash


class Concept(BaseModel):
    preferred_label: str = Field(..., description="The preferred label for the concept")
    description: str = Field(
        None,
        description=(
            "An optional description of the concept with enough detail to disambiguate "
            "it from similar concepts"
        ),
    )
    alternative_labels: List[str] = Field(
        [], description="A list of alternative labels for the concept"
    )
    examples: List[str] = Field(
        [], description="Positive examples of the concept in passages of text"
    )

    @property
    def all_labels(self) -> List[str]:
        return [self.preferred_label] + self.alternative_labels

    def __repr__(self) -> str:
        return f"Concept({self.preferred_label})"

    @computed_field(return_type=str)
    @property
    def id(self) -> str:
        return pretty_hash(self.preferred_label)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @classmethod
    def load(cls, file_path: Union[str, Path]):
        with open(file_path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save(self, file_path: Union[str, Path]):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @computed_field(return_type=str)
    @property
    def type(self) -> str:
        return "concept"
