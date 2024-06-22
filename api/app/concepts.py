from elasticsearch import NotFoundError
from fastapi import APIRouter, HTTPException, Query, Request

from src.concept import Concept
from src.search.core import ConceptSearchEngine

from . import (
    APIResponse,
    elasticsearch_instance,
    get_base_url,
    get_next_page_url,
    get_previous_page_url,
)

router = APIRouter(prefix="/concepts")

search_engine = ConceptSearchEngine(
    elasticsearch=elasticsearch_instance, index_name="concepts"
)


@router.get("/")
async def get_concepts(
    request: Request,
    page: int = Query(1, ge=1, description="The page number to return"),
    pageSize: int = Query(
        10, ge=1, le=100, description="The number of items to return"
    ),
    query: str = Query(None, description="Search terms for full-text search"),
) -> APIResponse:
    base_url = get_base_url(request)
    next_page = get_next_page_url(base_url, page, pageSize, query=query)
    previous_page = get_previous_page_url(base_url, page, pageSize, query=query)
    search_response = search_engine.search(query, page, pageSize)

    return APIResponse(
        totalResults=search_response.total,
        nextPage=next_page if search_response.total > page * pageSize else None,
        previousPage=previous_page if page > 1 else None,
        results=search_response.results,
    )


@router.get("/{identifier}")
async def get_concept(identifier: str) -> Concept:
    try:
        return search_engine.get_item(identifier)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Concept {identifier} not found"
        ) from e
