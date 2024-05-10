"""
Index full documents into elasticsearch.

This script reads the raw text files from the data/raw/text directory, indexes them into
an index called "documents" in a locally running elasticsearch cluster.
The documents are indexed with "title" and "text" fields. Both fields are analyzed using
a custom analyzer that tokenizes the text, removes stopwords, stems/lemmatizes words,
and creates shingles (n-grams).
"""

from pathlib import Path

from elasticsearch import Elasticsearch
from rich.console import Console
from rich.progress import track

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
        "title": {"type": "text", "analyzer": "english_analyzer"},
        "text": {"type": "text", "analyzer": "english_analyzer"},
        "concepts": {"type": "keyword"},
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

data_dir = Path("data/processed/documents")
files = list(data_dir.glob("*.json"))

for file in track(
    files, description="Indexing documents", console=console, transient=True
):
    document = Document.load(file)
    es.index(
        index=index_name,
        id=document.id,
        document=document.model_dump(),
    )


console.print(f"✅ indexed {len(files)} documents", style="green")
