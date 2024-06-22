import json
from typing import List, Optional

from elasticsearch import Elasticsearch

from src.concept import Concept
from src.document import Document
from src.search import SearchEngine, SearchResponse


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

    def _build_query(self, search_terms: Optional[str], concepts: List[str] = []):
        core_query = self.query if search_terms else {"match_all": {}}
        query = query = {
            "bool": {
                "should": [core_query],
                "filter": [],
            }
        }
        if search_terms:
            query = json.loads(
                json.dumps(self.query).replace("{{search_terms}}", search_terms)
            )

        if concepts:
            query["bool"]["filter"].append({"terms": {"concepts": concepts}})

        return query

    def insert_item(self, item: Document):
        self.elasticsearch.index(
            index=self.index_name, id=item.id, document=item.model_dump()
        )

    def search(
        self,
        search_terms: Optional[str],
        page: int = 1,
        page_size: int = 10,
        concepts: List[str] = [],
    ) -> SearchResponse:
        query = self._build_query(search_terms, concepts)
        response = self.elasticsearch.search(
            index=self.index_name,
            query=query,
            from_=(page - 1) * page_size,
            size=page_size,
        )

        return SearchResponse(
            total=response["hits"]["total"]["value"],
            results=[Document(**hit["_source"]) for hit in response["hits"]["hits"]],
        )

    def get_item(self, id: str) -> Document:
        response = self.elasticsearch.get(index=self.index_name, id=id)
        document = Document(**response["_source"])
        return document


class ConceptSearchEngine(SearchEngine):
    def __init__(self, elasticsearch: Elasticsearch, index_name: str = "concepts"):
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
                "preferred_label": {"type": "text", "analyzer": "english_analyzer"},
                "description": {"type": "text", "analyzer": "english_analyzer"},
                "alternative_labels": {"type": "text", "analyzer": "english_analyzer"},
            }
        }
        self.query = {
            "multi_match": {
                "query": "{{search_terms}}",
                "fields": [
                    "id",
                    "preferred_label",
                    "description",
                    "alternative_labels",
                ],
            }
        }

        self.index_exists = self.elasticsearch.indices.exists(index=self.index_name)
        if not self.index_exists:
            self.elasticsearch.indices.create(
                index=self.index_name, settings=self.settings, mappings=self.mappings
            )

    def _build_query(self, search_terms: Optional[str]):
        core_query = self.query if search_terms else {"match_all": {}}
        query = query = {
            "bool": {
                "should": [core_query],
                "filter": [],
            }
        }

        if search_terms:
            query = json.loads(
                json.dumps(self.query).replace("{{search_terms}}", search_terms)
            )

        return query

    def insert_item(self, item: Concept):
        self.elasticsearch.index(
            index=self.index_name, id=item.id, document=item.model_dump()
        )

    def search(
        self,
        search_terms: Optional[str],
        page: int = 1,
        page_size: int = 10,
    ) -> SearchResponse:
        query = self._build_query(search_terms)
        response = self.elasticsearch.search(
            index=self.index_name,
            query=query,
            from_=(page - 1) * page_size,
            size=page_size,
        )

        return SearchResponse(
            total=response["hits"]["total"]["value"],
            results=[Concept(**hit["_source"]) for hit in response["hits"]["hits"]],
        )

    def get_item(self, id: str) -> Concept:
        response = self.elasticsearch.get(index=self.index_name, id=id)
        concept = Concept(**response["_source"])
        return concept
