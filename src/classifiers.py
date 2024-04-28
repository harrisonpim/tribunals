import pickle
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from elasticsearch import Elasticsearch

from src.concept import Concept
from src.document import Document, Span


class Classifier(ABC):
    """Abstract class for all classifier types."""

    def __init__(self, concept: Concept):
        self.concept = concept

    @abstractmethod
    def predict(self, document: Document) -> List[Span]:
        """Find spans which match the concept in the document text."""
        pass

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


class RegexClassifier(Classifier):
    """Classifier that uses regular expressions to find spans of text."""

    def predict(self, document: Document) -> List[Span]:
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


class ElasticsearchClassifier(Classifier):
    """Classifier that uses Elasticsearch to find spans of text."""

    def __init__(
        self,
        concept: Concept,
        index_name: str,
        es_client: Elasticsearch = Elasticsearch(),
    ):
        super().__init__(concept)
        self.es_client = es_client
        self.index_name = index_name

    def predict(self, document: Document) -> List[Span]:
        spans = []
        for search_term in self.concept.all_labels:
            results = self.es_client.search(
                index=self.index_name,
                query={
                    "bool": {
                        "must": [
                            {"match_phrase": {"text": search_term}},
                            # only search the document with the given id
                            {"ids": {"values": [document.id]}},
                        ]
                    }
                },
                highlight={
                    "fields": {"text": {}},
                    "number_of_fragments": 0,
                },
                size=1,
            )

        for hit in results["hits"]["hits"]:  # account for zero hits
            text = hit.get("highlight", {}).get("text", [""])[0]
            while "<em>" in text and "</em>" in text:
                # every time a match is found, remove the tag so that the index for the
                # next match is correct with respect to the original text
                start_index = text.find("<em>")
                text = text.replace("<em>", "", 1)

                end_index = text.find("</em>")
                text = text.replace("</em>", "", 1)

                spans.append(
                    Span(
                        start_index=start_index,
                        end_index=end_index,
                        identifier=self.concept.id,
                    )
                )

        return spans
