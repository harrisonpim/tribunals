import json
import warnings
from pathlib import Path
from typing import Union

from pydantic import Field, model_validator
from typing_extensions import Self

from src.passage import Page
from src.passage_group import PassageGroup


class Document(PassageGroup):
    """A document containing text with spans"""

    title: str = Field(..., description="The title of the document", repr=True)

    @model_validator(mode="after")
    def ensure_that_passages_have_same_document_id_as_parent_document(self) -> Self:
        for passage in self.passages:
            if passage.document_id is None:
                passage.document_id = self.id
            elif passage.document_id != self.id:
                raise ValueError(
                    f"The document ID of passage {passage.id} ({passage.document_id}) "
                    f"does not match the document ID ({self.id})"
                )
        return self

    def __repr__(self) -> str:
        n_pages = len(
            [passage for passage in self.passages if isinstance(passage, Page)]
        )
        return f"{self.name}(id={self.id}, title={self.title}, n_pages={n_pages})"

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def _validate_path(cls, file: Union[str, Path]) -> None:
        file = Path(file)
        if file.suffix != ".json":
            warnings.warn("File does not have .json extension")

    @classmethod
    def load(cls, file: Union[str, Path]) -> "Document":
        """Loads a document from a json file with pre-structured document data

        :param Union[str, Path] file: The path to the json file
        :raises ValueError: If the file is not a json file
        :return Document: The loaded document
        """
        cls._validate_path(file)
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    def save(self, file: Union[str, Path]) -> None:
        """Saves the document to a file

        :param Union[str, Path] file: The path to save the document to
        :param str format: The format to save the document in, defaults to "json"
        :raises NotImplementedError: If the format is not supported
        """
        self._validate_path(file)
        with open(file, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load_from_raw(cls, file: Union[str, Path]) -> "Document":
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

        document = Document(title=title)
        index = 0
        for i, page in enumerate(data):
            page_number = i + 1
            document.passages.append(
                Page(
                    text=page,
                    number=page_number,
                    document_id=document.id,
                    start_index=index,
                    end_index=index + len(page),
                )
            )
            index += len(page)

        return document
