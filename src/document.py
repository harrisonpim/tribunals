import json
from pydantic import BaseModel
from pathlib import Path
from src.identifiers import pretty_hash


class Span(BaseModel):
    start: int
    end: int


class Document(BaseModel):
    title: str
    text: str
    pages: list[Span]

    def from_json(self, file: Path):
        with open(file, "r") as f:
            data = json.load(f)
            self.title = file.stem
            self.text = " ".join(data)
            self.pages = []
            for page_number, page in enumerate(data):
                self.pages.append(Span(start=page_number, end=page_number))

    def to_json(self, file: Path):
        with open(file, "w") as f:
            json.dump(self.model_dump(mode="json"), f)

    @property
    def id(self):
        return pretty_hash(
            {"title": self.title, "text": self.text, "n_pages": len(self.pages)}
        )
