"""
Index data into elasticsearch

Raw data (json files in data/processed as lists of strings) is indexed into 
elasticsearch. each string is a page, so we increment the page number for each string 
in the list.
"""

from rich.console import Console
from rich.progress import track

from pathlib import Path
from elasticsearch import Elasticsearch
from src.document import Document

console = Console()

settings = {
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
mappings = {
    "properties": {
        "document": {
            "properties": {
                "title": {"type": "text", "analyzer": "english_analyzer"},
                "id": {"type": "keyword"},
            },
        },
        "page": {
            "properties": {
                "number": {"type": "integer"},
                "text": {"type": "text", "analyzer": "english_analyzer"},
            },
        },
    }
}

es = Elasticsearch(
    hosts=[{"host": "localhost", "port": 9200}],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)

index_name = "documents"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    console.print(f"🚽 deleted existing index: {index_name}", style="yellow")

es.indices.create(index=index_name, settings=settings, mappings=mappings, ignore=400)
console.print(f"✅ created index: {index_name}", style="green")

data_dir = Path("data/processed")
files = list(data_dir.glob("*.json"))

for file in track(
    files, description="Indexing documents", console=console, transient=True
):
    document = Document.load(file)
    for page_number, page in enumerate(document.pages):
        es.index(
            index=index_name,
            id=f"{document.id}_{page_number}",
            document={
                "document": {"title": document.title, "id": document.id},
                "page": {"number": page_number, "text": page},
            },
        )

total_pages = es.count(index=index_name).get("count", 0)
console.print(
    f"✅ indexed {len(files)} documents with {total_pages} individual pages",
    style="green",
)
