import os
from typing import Dict, List

from elasticsearch import Elasticsearch
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.document import Document

router = APIRouter(prefix="/documents")

INDEX_NAME = "documents"

es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


class DocumentHit(Document):
    id: str
    type: str = "document"


class DocumentResponse(BaseModel):
    total: int
    results: List[DocumentHit]


def elasticsearch_hit_to_document_response(hit: Dict) -> DocumentHit:
    return DocumentHit(id=hit["_id"], **hit["_source"])


@router.get("/")
async def read_documents(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
) -> DocumentResponse:
    res = es.search(
        index=INDEX_NAME,
        body={"query": {"match_all": {}}},
        from_=(page - 1) * pageSize,
        size=pageSize,
        sort=["_id"],
    )
    return {
        "totalResults": res.get("hits", {}).get("total", {}).get("value", 0),
        "nextPage": f"{request.url}?page={page+1}&pageSize={pageSize}",
        "results": [
            elasticsearch_hit_to_document_response(hit)
            for hit in res.get("hits", {}).get("hits", [])
        ],
    }


@router.get("/{identifier}")
async def read_document(identifier: str) -> DocumentHit:
    res = es.get(index=INDEX_NAME, id=identifier)
    if res["found"]:
        return elasticsearch_hit_to_document_response(res)
    raise HTTPException(status_code=404, detail="Item not found")
