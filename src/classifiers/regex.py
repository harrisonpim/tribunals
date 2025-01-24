import re

from src.classifiers.classifier import Classifier
from src.passage import ConceptMention, Passage


class RegexClassifier(Classifier):
    """Classifier that uses regular expressions to find spans of text."""

    def predict(self, passage: Passage) -> list[ConceptMention]:
        """
        Predict spans in a passage using regular expressions.

        :param Passage passage: The passage group to classify
        :return list[ConceptMention]: A list of concept mentions in the passage group
        """
        mentions = []

        for label in self.concept.all_labels:
            pattern = r"\b{}\b".format(re.escape(label.lower()))
            for match in re.finditer(pattern, passage.text.lower()):
                mentions.append(
                    ConceptMention(
                        start_index=match.start(),
                        end_index=match.end(),
                        concept_id=self.concept.id,
                        text=passage.text,
                        document_id=passage.document_id,
                        zoom_level=1,
                    )
                )
        return mentions
