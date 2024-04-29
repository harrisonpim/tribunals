from typing import List

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.document import Document, Span


class SetFitClassifier(Classifier):
    """
    https://github.com/huggingface/setfit
    """

    def __init__(self, concept: Concept):
        raise NotImplementedError

    def predict(self, document: Document) -> List[Span]:
        raise NotImplementedError
