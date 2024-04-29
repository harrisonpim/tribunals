from typing import List

from elasticsearch import Elasticsearch

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.document import Document, Span


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
