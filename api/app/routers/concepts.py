import os

from elasticsearch import Elasticsearch
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/concepts",
    tags=["concepts"],
    responses={404: {"description": "Not found"}},
)

INDEX_NAME = "concepts"
es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


@router.get("/")
async def read_concepts():
    res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    return res


@router.get("/{identifier}")
async def read_concept(identifier: str):
    res = es.get(index=INDEX_NAME, id=identifier)
    if res["found"]:
        return res["_source"]
    raise HTTPException(status_code=404, detail="Item not found")
