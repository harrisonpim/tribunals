"""Index full documents into elasticsearch"""

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

data_dir = Path("data/raw/text")
files = list(data_dir.glob("*.json"))

for file in track(
    files, description="Indexing documents", console=console, transient=True
):
    document = Document.load_raw(file)
    es.index(
        index=index_name,
        id=document.id,
        document={
            "title": document.title,
            "text": document.text,
        },
    )


console.print(f"✅ indexed {len(files)} documents", style="green")
