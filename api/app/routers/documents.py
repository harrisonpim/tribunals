import os

from elasticsearch import Elasticsearch
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

INDEX_NAME = "documents"
es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


@router.get("/")
async def read_documents():
    res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    return res


@router.get("/{identifier}")
async def read_document(identifier: str):
    res = es.get(index=INDEX_NAME, id=identifier)
    if res["found"]:
        return res["_source"]
    raise HTTPException(status_code=404, detail="Item not found")
