import json
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel

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
