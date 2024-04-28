"""
Index sentences into elasticsearch.


This script reads the raw text files from the data/raw/text directory, splits them into
sentences, and indexes each sentence as a separate document into an index called
"sentences" in a locally running elasticsearch cluster.

The indexed sentences have a structure like:
{
    "document": {
        "title": "document title",
        "id": "document id"
    },
    "sentence": {
        "number": 0,
        "text": "sentence text"
    }
}

The ID of each sentence is a combination of the document ID and the sentence number.
"document.title" and "sentence.text" fields are analyzed using a custom analyzer that
tokenizes the text, removes stopwords, stems/lemmatizes words, and creates shingles
(n-grams).
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
        "document": {
            "properties": {
                "title": {"type": "text", "analyzer": "english_analyzer"},
                "id": {"type": "keyword"},
            },
        },
        "sentence": {
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

index_name = "sentences"

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
    for sentence_number, sentence in enumerate(document.sentences):
        es.index(
            index=index_name,
            id=f"{document.id}_{sentence_number}",
            document={
                "document": {"title": document.title, "id": document.id},
                "sentence": {"number": sentence_number, "text": sentence},
            },
        )

total_sentences = es.count(index=index_name).get("count", 0)
console.print(
    f"✅ indexed {len(files)} documents with {total_sentences} individual sentences",
    style="green",
)
