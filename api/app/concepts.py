import os
from typing import Dict, List, Optional

from elasticsearch import Elasticsearch, NotFoundError
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.concept import Concept

from . import default_page_size

router = APIRouter(prefix="/concepts")

INDEX_NAME = "concepts"
es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


class ConceptResponse(BaseModel):
    totalResults: int = Field(..., description="The total number of results")
    nextPage: Optional[str] = Field(
        None, description="The URL for the next page of results"
    )
    previousPage: Optional[str] = Field(
        None, description="The URL for the previous page of results"
    )
    results: List[Concept]


def elasticsearch_hit_to_concept_response(hit: Dict) -> Concept:
    return Concept(id=hit["_id"], **hit["_source"])


@router.get("/")
async def read_concepts(
    request: Request,
    page: int = Query(1, ge=1, description="The page number to return"),
    pageSize: int = Query(
        10, ge=1, le=100, description="The number of items to return"
    ),
    query: str = Query(None, description="Search terms for full-text search"),
) -> ConceptResponse:
    base_url = request.url.scheme + "://" + request.url.netloc + request.url.path

    if query:
        res = es.search(
            index=INDEX_NAME,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "preferred_label",
                            "alternative_labels",
                            "description",
                        ],
                    }
                }
            },
            from_=(page - 1) * pageSize,
            size=pageSize,
        )
    else:
        res = es.search(
            index=INDEX_NAME,
            body={"query": {"match_all": {}}},
            from_=(page - 1) * pageSize,
            size=pageSize,
            sort=["_id"],
        )

    results = [
        elasticsearch_hit_to_concept_response(hit)
        for hit in res.get("hits", {}).get("hits", [])
    ]

    # add metadata to response
    totalResults = res.get("hits", {}).get("total", {}).get("value", 0)
    response = {
        "totalResults": totalResults,
        "results": results,
    }

    if totalResults > page * pageSize:
        nextpage = f"{base_url}?page={page + 1}"
        if pageSize != default_page_size:
            nextpage += f"&pageSize={pageSize}"
        if query:
            nextpage += f"&query={query}"
        response["nextPage"] = nextpage

    if page > 1:
        previouspage = f"{base_url}?page={page - 1}"
        if pageSize != default_page_size:
            previouspage += f"&pageSize={pageSize}"
        if query:
            previouspage += f"&query={query}"
        response["previousPage"] = previouspage

    return response


@router.get("/{identifier}")
async def read_concept(identifier: str) -> Concept:
    try:
        res = es.get(index=INDEX_NAME, id=identifier)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Concept {identifier} not found"
        ) from e
    return elasticsearch_hit_to_concept_response(res)
