from pydantic import BaseModel, Field, computed_field

from src.identifiers import Identifier
from src.passage import ConceptMention, Passage
from src.rag import rag
from src.summarisation import summarise


class PassageGroup(BaseModel):
    """Base class for a group of passages"""

    passages: list[Passage] = Field(
        default_factory=list,
        description="A list of passages representing the passages within the text",
        repr=False,
    )

    @computed_field(repr=True)
    @property
    def id(self) -> Identifier:
        """Generate a unique identifier for this passage group"""
        texts = sorted([passage.text for passage in self.passages])
        return Identifier.generate("".join(texts))

    @computed_field(repr=True)
    @property
    def n_passages(self) -> int:
        """Get the number of passages in the passage group"""
        return len(self.passages)

    def get_passages_at_zoom_level(self, zoom_level: int) -> "PassageGroup":
        """Get all passages at a specific zoom level"""
        filtered_passages = list(
            filter(lambda passage: passage.zoom_level == zoom_level, self.passages)
        )
        return PassageGroup(passages=filtered_passages)

    @computed_field(repr=False)
    @property
    def concept_ids(self) -> list[Identifier]:
        """Get the identifiers of concepts found in the text"""
        return [
            passage.concept_id
            for passage in self.passages
            if isinstance(passage, ConceptMention)
        ]

    @computed_field(repr=False)
    @property
    def document_ids(self) -> list[Identifier]:
        """Get the identifiers of documents found in the passage group"""
        return sorted(
            list(
                set(
                    [
                        passage.document_id
                        for passage in self.passages
                        if passage.document_id
                    ]
                )
            )
        )

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.name}(id={self.id})"

    def __str__(self) -> str:
        return self.__repr__()

    @computed_field(repr=False)
    @property
    def text(self) -> str:
        """Get all of the text contained in the passage group"""
        return "\n".join([passage.text for passage in self.passages])

    def summarise(self) -> str:
        """Generate a summary of the passage group"""
        return summarise(self)

    def ask_a_question(self, question: str) -> str:
        """RAG query for the passage group"""
        return rag(self, question)
