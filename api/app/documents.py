import os
from typing import Dict, List

from elasticsearch import Elasticsearch
from fastapi import APIRouter, HTTPException

from src.document import Document

router = APIRouter(prefix="/documents")

INDEX_NAME = "documents"

es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


class DocumentResponse(Document):
    id: str
    type: str = "document"


def elasticsearch_hit_to_document_response(hit: Dict) -> DocumentResponse:
    return DocumentResponse(id=hit["_id"], **hit["_source"])


@router.get("/")
async def read_documents() -> List[DocumentResponse]:
    res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    return [elasticsearch_hit_to_document_response(hit) for hit in res["hits"]["hits"]]


@router.get("/{identifier}")
async def read_document(identifier: str):
    res = es.get(index=INDEX_NAME, id=identifier)
    if res["found"]:
        return elasticsearch_hit_to_document_response(res)
    raise HTTPException(status_code=404, detail="Item not found")
