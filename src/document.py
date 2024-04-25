import warnings
from typing import Union, Optional
import json
from pydantic import BaseModel
from pathlib import Path
from src.identifiers import pretty_hash


class Span(BaseModel):
    """A span of text within a document"""

    start_index: int
    end_index: int
    identifier: Optional[str] = None


class Document(BaseModel):
    """Base class for a document"""

    title: str
    text: str
    page_spans: list[Span]
    concept_spans: list[Span] = []
    sentence_spans: list[Span] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.sentence_spans = self._get_sentence_spans()

    @classmethod
    def load(cls, file: Union[str, Path]):
        """
        Loads a document from a json file

        :param Union[str, Path] file: The path to the json file
        :raises ValueError: If the file is not a json file
        :return Document: The loaded document
        """
        file = Path(file)
        if file.suffix != ".json":
            raise ValueError(f"File must be a json file: {file}")

        with open(file, "r") as f:
            data = json.load(f)

        title = file.stem
        text = "".join(data)
        page_spans = []
        index = 0
        for page in data:
            page_spans.append(Span(start_index=index, end_index=index + len(page)))
            index += len(page)

        return cls(title=title, text=text, page_spans=page_spans)

    def save(self, file: Union[str, Path], format: str = "json"):
        """
        Saves the document to a file

        :param Union[str, Path] file: The path to save the document to
        :param str format: The format to save the document in, defaults to "json"
        :raises NotImplementedError: If the format is not supported
        """
        file = Path(file)
        if format == "json":
            if file.suffix != ".json":
                warnings.warn("File does not have .json extension")
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.model_dump(mode="json"), f)
        else:
            raise NotImplementedError(f"Format {format} not implemented")

    def _get_sentence_spans(self):
        """
        Get the spans of the sentences in the document

        :return list[Span]: The spans of the sentences
        """
        sentence_spans = []
        index = 0
        for sentence in self.text.split("."):
            sentence_spans.append(
                Span(start_index=index, end_index=index + len(sentence))
            )
            index += len(sentence) + 1
        return sentence_spans

    @property
    def id(self):
        return pretty_hash(
            {"title": self.title, "text": self.text, "n_pages": len(self.pages)}
        )

    @property
    def pages(self):
        return [
            self.text[span.start_index : span.end_index] for span in self.page_spans
        ]

    @property
    def sentences(self):
        return [
            self.text[span.start_index : span.end_index] for span in self.sentence_spans
        ]

    @property
    def concepts(self):
        return list(set([span.identifier for span in self.concept_spans]))

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title}, n_pages={len(self.pages)})"
