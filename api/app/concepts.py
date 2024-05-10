import os
from typing import Dict, List

from elasticsearch import Elasticsearch
from fastapi import APIRouter, HTTPException

from src.concept import Concept

router = APIRouter(prefix="/concepts")

INDEX_NAME = "concepts"
es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


class ConceptResponse(Concept):
    id: str
    type: str = "concept"


def elasticsearch_hit_to_concept_response(hit: Dict) -> ConceptResponse:
    return ConceptResponse(id=hit["_id"], **hit["_source"])


@router.get("/")
async def read_concepts() -> List[ConceptResponse]:
    res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    return [elasticsearch_hit_to_concept_response(hit) for hit in res["hits"]["hits"]]


@router.get("/{identifier}")
async def read_concept(identifier: str) -> ConceptResponse:
    res = es.get(index=INDEX_NAME, id=identifier)
    if res["found"]:
        return elasticsearch_hit_to_concept_response(res)
    raise HTTPException(status_code=404, detail="Item not found")
