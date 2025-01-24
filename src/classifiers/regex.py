import re

from src.classifiers.classifier import Classifier
from src.document import Document
from src.passage import Passage


class RegexClassifier(Classifier):
    """Classifier that uses regular expressions to find spans of text."""

    def predict(self, document: Document) -> list[Passage]:
        """
        Predict spans in a document using regular expressions.

        :param Document document: The document to classify
        :return list[Passage]: A list of passages in the document
        """
        passages = []
        for label in self.concept.all_labels:
            pattern = r"\b{}\b".format(re.escape(label.lower()))
            for match in re.finditer(pattern, document.text.lower()):
                passages.append(
                    Passage(
                        start_index=match.start(),
                        end_index=match.end(),
                        identifier=self.concept.id,
                        text=document.text[match.start() : match.end()],
                    )
                )
        return passages
