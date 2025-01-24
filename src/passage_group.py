from pydantic import BaseModel, Field, computed_field

from src.identifiers import Identifier
from src.passage import ConceptMention, Passage


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

    def get_passages_at_zoom_level(self, zoom_level: int) -> list[Passage]:
        """Get all passages at a specific zoom level"""
        return list(
            filter(lambda passage: passage.zoom_level == zoom_level, self.passages)
        )

    @computed_field(repr=False)
    @property
    def concept_ids(self) -> list[Identifier]:
        """Get the identifiers of concepts found in the text"""
        return [
            passage.concept_id
            for passage in self.passages
            if isinstance(passage, ConceptMention)
        ]

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.name}(id={self.id})"

    def __str__(self) -> str:
        return self.__repr__()

    def generate_summary(self) -> str:
        """Generate a summary of the passage group"""
        if self.get_passages_at_zoom_level(0):
            return "This is a summary of the raw text"
        else:
            raise ValueError("No passages to generate summary from")
