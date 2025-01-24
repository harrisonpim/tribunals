import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from src.concept import Concept
from src.passage import ConceptMention, Passage


class Classifier(ABC):
    """Abstract class for all classifier types."""

    def __init__(self, concept: Concept):
        self.concept = concept

    def fit(self) -> "Classifier":
        """
        Train the classifier on the data in the concept.

        :return Classifier: The trained classifier
        """
        return self

    @abstractmethod
    def predict(self, passage: Passage) -> list[ConceptMention]:
        """
        Predict spans which match the concept in the passage text.

        :param Passage passage: The passage to classify
        :return list[ConceptMention]: A list of concept mentions in the passage
        """
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.concept.preferred_label})"

    def __str__(self) -> str:
        return self.__repr__()

    def save(self, path: Union[str, Path]):
        """
        Save the classifier to a file.

        :param Union[str, Path] path: The path to save the classifier to
        """
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Classifier":
        """
        Load a classifier from a file.

        :param Union[str, Path] path: The path to load the classifier from
        :return Classifier: The loaded classifier
        """
        with open(path, "rb") as f:
            classifier = pickle.load(f)
        assert isinstance(classifier, Classifier)
        return classifier
