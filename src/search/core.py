import json
from typing import List

from elasticsearch import Elasticsearch

from src.document import Document
from src.search import SearchEngine


class DocumentSearchEngine(SearchEngine):
    def __init__(self, elasticsearch: Elasticsearch, index_name: str = "documents"):
        self.elasticsearch = elasticsearch
        self.index_name = index_name

        self.settings = {
            "analysis": {
                "analyzer": {
                    "english_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_token_filter",
                            "english_possessive_token_filter",
                            "shingle_token_filter",
                            "asciifolding_token_filter",
                        ],
                    },
                },
                "filter": {
                    "asciifolding_token_filter": {
                        "type": "asciifolding",
                        "preserve_original": True,
                    },
                    "shingle_token_filter": {
                        "type": "shingle",
                        "max_shingle_size": 4,
                        "min_shingle_size": 2,
                    },
                    "english_token_filter": {"type": "stemmer", "name": "english"},
                    "english_possessive_token_filter": {
                        "type": "stemmer",
                        "name": "possessive_english",
                    },
                },
                "normalizer": {
                    "lowercase_normalizer": {"type": "custom", "filter": ["lowercase"]}
                },
            }
        }
        self.mappings = {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "english_analyzer"},
                "text": {"type": "text", "analyzer": "english_analyzer"},
                "summary": {"type": "text", "analyzer": "english_analyzer"},
                "concepts": {"type": "keyword"},
            }
        }
        self.query = {
            "multi_match": {
                "query": "{{search_terms}}",
                "fields": ["id", "title", "text", "summary", "concepts"],
            }
        }
        self.index_exists = self.elasticsearch.indices.exists(index=self.index_name)
        if not self.index_exists:
            self.elasticsearch.indices.create(
                index=self.index_name, settings=self.settings, mappings=self.mappings
            )

    def _build_query(self, search_terms: str):
        return json.loads(
            json.dumps(self.query).replace("{{search_terms}}", search_terms)
        )

    def add_document(self, document: Document):
        self.elasticsearch.index(
            index=self.index_name, id=document.id, document=document.model_dump()
        )

    def search(self, search_terms: str, n: int) -> List[Document]:
        response = self.elasticsearch.search(
            index=self.index_name, query=self._build_query(search_terms), size=n
        )
        results = [Document(**hit["_source"]) for hit in response["hits"]["hits"]]
        return results

    def get_document(self, id: str) -> Document:
        response = self.elasticsearch.get(index=self.index_name, id=id)
        document = Document(**response["_source"])
        return document
