from typing import List

from setfit import SetFitModel

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.document import Document
from src.span import Span


class SetFitClassifier(Classifier):
    """
    https://github.com/huggingface/setfit
    """

    def __init__(self, concept: Concept, model_name: str = "BAAI/bge-small-en-v1.5"):
        super().__init__(concept)
        self.model = SetFitModel.from_pretrained(model_name)

    def fit(self) -> "SetFitClassifier":
        raise NotImplementedError

    def predict(self, document: Document) -> List[Span]:
        raise NotImplementedError
