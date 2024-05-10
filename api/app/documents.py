import os
from typing import List, Optional

from elasticsearch import Elasticsearch, NotFoundError
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.document import Document

from . import default_page_size, format_response_metadata

router = APIRouter(prefix="/documents")

INDEX_NAME = "documents"

es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


class DocumentResponse(BaseModel):
    totalResults: int = Field(..., description="The total number of results")
    nextPage: Optional[str] = Field(
        None, description="The URL for the next page of results"
    )
    previousPage: Optional[str] = Field(
        None, description="The URL for the previous page of results"
    )
    results: List[Document]


@router.get("/")
async def read_documents(
    request: Request,
    page: int = Query(1, ge=1, description="The page number to return"),
    pageSize: int = Query(
        default_page_size, ge=1, le=100, description="The number of items to return"
    ),
    query: str = Query(None, description="Search terms for full-text search"),
    concepts: Optional[List[str]] = Query(
        alias="concept",
        default=None,
        description=(
            "Filter documents by the IDs of the concepts that they mention. If "
            "multiple concept IDs are provided, documents may contain any of the "
            "concepts, ie. the filter is treated as an OR operation"
        ),
    ),
) -> DocumentResponse:
    base_url = request.url.scheme + "://" + request.url.netloc + request.url.path

    # get results from Elasticsearch
    query_parameters = {
        "index": INDEX_NAME,
        "size": pageSize,
        "from_": (page - 1) * pageSize,
        "body": {"query": {"bool": {"must": [{"match_all": {}}]}}},
    }

    if query:
        query_parameters["body"]["query"]["bool"]["must"] = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "text"],
                }
            }
        ]
    else:
        query_parameters.update(
            {
                "sort": ["_id"],
            }
        )
    if concepts:
        query_parameters["body"]["query"]["bool"]["must"].append(
            {"terms": {"concepts": concepts}}
        )

    res = es.search(**query_parameters)

    # format results
    results = [
        Document(**hit["_source"]) for hit in res.get("hits", {}).get("hits", [])
    ]
    response = format_response_metadata(
        res, base_url, page, pageSize, query, results, concepts
    )
    return response


@router.get("/{identifier}")
async def read_document(identifier: str) -> Document:
    try:
        res = es.get(index=INDEX_NAME, id=identifier)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Document {identifier} not found"
        ) from e
    return Document(**res["_source"])
