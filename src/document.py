import json
import warnings
from pathlib import Path
from typing import List, Optional, Union

import spacy
from pydantic import BaseModel, Field, computed_field, model_validator
from typing_extensions import Self

from src.identifiers import pretty_hash
from src.span import Span

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")


class Document(BaseModel):
    """Base class for a document"""

    title: str = Field(..., description="The title of the document")
    text: str = Field(..., description="The complete text of the document")
    summary: Optional[str] = Field(
        default=None,
        description="An LLM-generated summary of the document",
    )
    page_spans: List[Span] = Field(
        default=[], description="A list of spans representing the pages of the document"
    )
    concept_spans: List[Span] = Field(
        default=[],
        description=(
            "A list of spans representing appearances of concepts within the document"
        ),
    )
    sentence_spans: List[Span] = Field(
        default=[],
        description="A list of spans representing the sentences within the document",
    )

    def __init__(self, parse_sentences: bool = True, **data):
        super().__init__(**data)
        if parse_sentences:
            self.sentence_spans = self._get_sentence_spans()

    @classmethod
    def load_raw(cls, file: Union[str, Path], parse_sentences: bool = True):
        """Loads a document from a json file of raw text

        :param Union[str, Path] file: The path to the json file
        :param bool parse_sentences: Whether to split the document text into sentences
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
            page_spans.append(
                Span(start_index=index, end_index=index + len(page), type="page")
            )
            index += len(page)

        return cls(
            title=title,
            text=text,
            page_spans=page_spans,
            parse_sentences=parse_sentences,
        )

    @classmethod
    def load(cls, file: Union[str, Path], parse_sentences: bool = True):
        """Loads a document from a json file with pre-structured document data

        :param Union[str, Path] file: The path to the json file
        :param bool parse_sentences: Whether to split the document text into sentences
        :raises ValueError: If the file is not a json file
        :return Document: The loaded document
        """
        file = Path(file)
        if file.suffix != ".json":
            raise ValueError(f"File must be a json file: {file}")

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data, parse_sentences=parse_sentences)

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
                Span(
                    start_index=sent.start_char,
                    end_index=sent.end_char,
                    type="sentence",
                )
            )
        return sentence_spans

    @computed_field(return_type=str)
    @property
    def id(self):
        return pretty_hash(
            {"title": self.title, "text": self.text, "n_pages": len(self.page_spans)}
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

    @computed_field(return_type=List[str])
    @property
    def concepts(self):
        return [span.identifier for span in self.concept_spans]

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title}, n_pages={len(self.pages)})"

    @computed_field(return_type=str)
    @property
    def type(self) -> str:
        return "document"

    @model_validator(mode="after")
    def validate_spans(self) -> Self:
        """Ensures that all spans are within the bounds of the document text"""
        for span in self.page_spans + self.concept_spans + self.sentence_spans:
            if span.start_index < 0 or span.end_index > len(self.text):
                raise ValueError(f"Span {span} is out of bounds of the text")
        return self
