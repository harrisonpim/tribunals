import re
from abc import ABC, abstractmethod
from typing import List

from src.concept import Concept
from src.document import Span


class Classifier(ABC):
    """Abstract class for all classifier types."""

    def __init__(self, concept: Concept):
        self.concept = concept

    @abstractmethod
    def predict(self, text: str) -> List[Span]:
        """Predict the span of the text that is of interest."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.concept.preferred_label})"


class RegexClassifier(Classifier):
    """Classifier that uses regular expressions to find spans of text."""

    def predict(self, text: str) -> List[Span]:
        spans = []
        for label in self.concept.all_labels:
            pattern = r"\b{}\b".format(re.escape(label.lower()))
            for match in re.finditer(pattern, text.lower()):
                spans.append(
                    Span(
                        start_index=match.start(),
                        end_index=match.end(),
                        identifier=self.concept.id,
                    )
                )
        return spans
