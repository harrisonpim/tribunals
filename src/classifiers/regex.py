import re
from typing import List

from src.classifiers.classifier import Classifier
from src.document import Document, Span


class RegexClassifier(Classifier):
    """Classifier that uses regular expressions to find spans of text."""

    def predict(self, document: Document) -> List[Span]:
        """
        Predict spans in a document using regular expressions.

        :param Document document: The document to classify
        :return List[Span]: A list of spans in the document
        """
        spans = []
        for label in self.concept.all_labels:
            pattern = r"\b{}\b".format(re.escape(label.lower()))
            for match in re.finditer(pattern, document.text.lower()):
                spans.append(
                    Span(
                        start_index=match.start(),
                        end_index=match.end(),
                        identifier=self.concept.id,
                    )
                )
        return spans
