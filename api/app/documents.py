from typing import Optional

from elasticsearch import NotFoundError
from fastapi import APIRouter, HTTPException, Query, Request

from src.document import Document
from src.search.core import DocumentSearchEngine

from . import (
    APIResponse,
    default_page_size,
    elasticsearch_instance,
    get_base_url,
    get_next_page_url,
    get_previous_page_url,
)

router = APIRouter(prefix="/documents")

search_engine = DocumentSearchEngine(
    elasticsearch=elasticsearch_instance, index_name="documents"
)


@router.get("/")
async def get_documents(
    request: Request,
    page: int = Query(default=1, ge=1, description="The page number to return"),
    pageSize: int = Query(
        default=default_page_size,
        ge=1,
        le=100,
        description="The number of items to return",
    ),
    query: str = Query(
        None, description="Search terms for full-text search", example="covid-19"
    ),
    concepts: Optional[str] = Query(
        default=None,
        description=(
            "Filter documents by the IDs of the concepts that they mention. If "
            "multiple concept IDs are provided, documents may contain any of the "
            "concepts, ie. the filter is treated as an OR operation. Concept IDs "
            "should be provided as a comma-separated list."
        ),
        openapi_examples={
            "filter_by_a_single_concept": {
                "summary": "Filter by a single concept",
                "value": "68t56e7d",
            },
            "filter_by_multiple_concepts": {
                "summary": "Filter by multiple concepts",
                "value": "68t56e7d,vfbhyncy",
            },
        },
    ),
) -> APIResponse:
    parsed_concepts = concepts.split(",") if concepts else []
    base_url = get_base_url(request)
    next_page = get_next_page_url(
        base_url, page, pageSize, query=query, concepts=concepts
    )
    previous_page = get_previous_page_url(
        base_url, page, pageSize, query=query, concepts=concepts
    )
    search_response = search_engine.search(
        search_terms=query, page=page, page_size=pageSize, concepts=parsed_concepts
    )

    return APIResponse(
        totalResults=search_response.total,
        nextPage=next_page if search_response.total > page * pageSize else None,
        previousPage=previous_page if page > 1 else None,
        results=search_response.results,
    )


@router.get("/{identifier}")
async def get_document(identifier: str) -> Document:
    try:
        return search_engine.get_item(identifier)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Document {identifier} not found"
        ) from e
