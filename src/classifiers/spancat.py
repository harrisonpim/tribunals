from typing import List

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.document import Document, Span


class SpanCatClassifier(Classifier):
    """
    https://spacy.io/api/spancategorizer
    """

    def __init__(self, concept: Concept):
        raise NotImplementedError

    def predict(self, document: Document) -> List[Span]:
        raise NotImplementedError
