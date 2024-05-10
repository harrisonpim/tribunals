import os
from typing import Dict, List, Optional

from elasticsearch import Elasticsearch, NotFoundError
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.document import Document

from . import default_page_size

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


def elasticsearch_hit_to_document_response(hit: Dict) -> Document:
    return Document(id=hit["_id"], **hit["_source"])


@router.get("/")
async def read_documents(
    request: Request,
    page: int = Query(1, ge=1, description="The page number to return"),
    pageSize: int = Query(
        default_page_size, ge=1, le=100, description="The number of items to return"
    ),
    query: str = Query(None, description="Search terms for full-text search"),
) -> DocumentResponse:
    base_url = request.url.scheme + "://" + request.url.netloc + request.url.path

    # get results from Elasticsearch
    if query:
        res = es.search(
            index=INDEX_NAME,
            body={
                "query": {"multi_match": {"query": query, "fields": ["title", "text"]}}
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

    # format results
    results = [
        elasticsearch_hit_to_document_response(hit)
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
async def read_document(identifier: str) -> Document:
    try:
        res = es.get(index=INDEX_NAME, id=identifier)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Document {identifier} not found"
        ) from e
    return elasticsearch_hit_to_document_response(res)
