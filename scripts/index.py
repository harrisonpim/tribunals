"""
Index data into elasticsearch

Raw data (json files in data/processed as lists of strings) is indexed into 
elasticsearch. each string is a page, so we increment the page number for each string 
in the list.
"""

from pathlib import Path
import json
from elasticsearch import Elasticsearch

mapping = {
    "mappings": {
        "properties": {
            "document": {
                "type": "object",
                "properties": {"title": {"type": "text"}, "text": {"type": "text"}},
            },
            "page": {
                "type": "object",
                "properties": {"number": {"type": "integer"}, "text": {"type": "text"}},
            },
        }
    }
}


es = Elasticsearch()

if not es.indices.exists(index="documents"):
    es.indices.create(index="documents", body=mapping)


data_dir = Path("data/processed")

for file in data_dir.iterdir():
    with open(file, "r") as f:
        data = json.load(f)
        document_title = file.stem
        document_text = " ".join(data)
        for page_number, page in enumerate(data):
            es.index(
                index="documents",
                id=page_number,
                body={
                    "document": {"title": document_title, "text": document_text},
                    "page": {"number": page_number, "text": page},
                },
            )
