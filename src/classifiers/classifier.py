import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from src.concept import Concept
from src.document import Document, Span


class Classifier(ABC):
    """Abstract class for all classifier types."""

    def __init__(self, concept: Concept):
        self.concept = concept

    @abstractmethod
    def predict(self, document: Document) -> List[Span]:
        """Find spans which match the concept in the document text."""
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.concept.preferred_label})"

    def save(self, path: Union[str, Path]):
        """Save the classifier to a file."""
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]):
        """Load a classifier from a file."""
        with open(path, "rb") as f:
            classifier = pickle.load(f)
        assert isinstance(classifier, Classifier)
        return classifier
