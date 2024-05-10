import json
import warnings
from pathlib import Path
from typing import List, Optional, Union

import spacy
from pydantic import BaseModel, Field

from src.identifiers import pretty_hash

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")


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


class Document(BaseModel):
    """Base class for a document"""

    title: str = Field(..., description="The title of the document")
    text: str = Field(..., description="The complete text of the document")
    page_spans: List[Span] = Field(
        [], description="A list of spans representing the pages of the document"
    )
    concept_spans: List[Span] = Field(
        [],
        description=(
            "A list of spans representing appearances of concepts within the document"
        ),
    )
    sentence_spans: List[Span] = Field(
        [], description="A list of spans representing the sentences within the document"
    )

    def __init__(self, parse: bool = True, **data):
        super().__init__(**data)
        if parse:
            self.sentence_spans = self._get_sentence_spans()

    @classmethod
    def load_raw(cls, file: Union[str, Path], parse: bool = True):
        """Loads a document from a json file of raw text

        :param Union[str, Path] file: The path to the json file
        :raises ValueError: If the file is not a json file
        :return Document: The loaded document
        """
        file = Path(file)
        if file.suffix != ".json":
            raise ValueError(f"File must be a json file: {file}")

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        title = file.stem
        text = "".join(data)
        page_spans = []
        index = 0
        for page in data:
            page_spans.append(Span(start_index=index, end_index=index + len(page)))
            index += len(page)

        return cls(title=title, text=text, page_spans=page_spans, parse=parse)

    @classmethod
    def load(cls, file: Union[str, Path]):
        """Loads a document from a json file with pre-structured document data

        :param Union[str, Path] file: The path to the json file
        :raises ValueError: If the file is not a json file
        :return Document: The loaded document
        """
        file = Path(file)
        if file.suffix != ".json":
            raise ValueError(f"File must be a json file: {file}")

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    def save(self, file: Union[str, Path]):
        """Saves the document to a file

        :param Union[str, Path] file: The path to save the document to
        :param str format: The format to save the document in, defaults to "json"
        :raises NotImplementedError: If the format is not supported
        """
        file = Path(file)
        if file.suffix != ".json":
            warnings.warn("File does not have .json extension")
        with open(file, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    def _get_sentence_spans(self):
        """Get the spans of the sentences in the document

        :return list[Span]: The spans of the sentences
        """
        doc = nlp(self.text)
        sentence_spans = []
        for sent in doc.sents:
            sentence_spans.append(
                Span(start_index=sent.start_char, end_index=sent.end_char)
            )
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
        return [span.identifier for span in self.concept_spans]

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title}, n_pages={len(self.pages)})"

    @property
    def type(self) -> str:
        return "document"
