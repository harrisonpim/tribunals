from pydantic import BaseModel
from typing import List
from src.identifiers import pretty_hash


class Concept(BaseModel):
    preferred_label: str
    description: str
    alternative_labels: List[str]

    @property
    def all_labels(self) -> List[str]:
        return [self.preferred_label] + self.alternative_labels

    def __repr__(self) -> str:
        return f"Concept({self.preferred_label})"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @property
    def id(self) -> str:
        return pretty_hash(self.preferred_label)
