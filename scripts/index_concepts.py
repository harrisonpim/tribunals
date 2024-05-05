"""
Index concepts into elasticsearch.

This script reads the raw text files from the data/processed/concepts directory, and
indexes them into an index called "concepts" in a locally running elasticsearch cluster.
"""

from pathlib import Path

from elasticsearch import Elasticsearch
from rich.console import Console
from rich.progress import track

from src.concept import Concept

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
        "preferred_label": {"type": "text", "analyzer": "english_analyzer"},
        "alternative_labels": {"type": "text", "analyzer": "english_analyzer"},
        "description": {"type": "text", "analyzer": "english_analyzer"},
    }
}

es = Elasticsearch(
    hosts=[{"host": "localhost", "port": 9200}],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)

index_name = "concepts"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    console.print(f"🚽 deleted existing index: {index_name}", style="yellow")

es.indices.create(index=index_name, settings=settings, mappings=mappings, ignore=400)
console.print(f"✅ created index: {index_name}", style="green")

data_dir = Path("data/processed/concepts")
files = list(data_dir.glob("*.json"))

for file in track(
    files, description="Indexing concepts", console=console, transient=True
):
    concept = Concept.load(file)
    es.index(
        index=index_name,
        id=concept.id,
        document=concept.model_dump(),
    )


console.print(f"✅ indexed {len(files)} concepts", style="green")
