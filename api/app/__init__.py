from typing import List, Optional, Union

from src.concept import Concept
from src.document import Document

default_page_size = 10


def format_response_metadata(
    res: dict,
    base_url: str,
    page: int,
    pageSize: int,
    query: Optional[str],
    results: Union[List[Document], List[Concept]],
    concepts: Optional[List[str]] = None,
):
    totalResults = res.get("hits", {}).get("total", {}).get("value", 0)
    response = {
        "totalResults": totalResults,
        "results": results,
    }

    if totalResults > page * pageSize:
        next_page = f"{base_url}?page={page + 1}"
        if pageSize != default_page_size:
            next_page += f"&pageSize={pageSize}"
        if query:
            next_page += f"&query={query}"
        if concepts:
            next_page += "".join([f"&concept={concept}" for concept in concepts])
        response["nextPage"] = next_page

    if page > 1:
        previous_page = f"{base_url}?page={page - 1}"
        if pageSize != default_page_size:
            previous_page += f"&pageSize={pageSize}"
        if query:
            previous_page += f"&query={query}"
        if concepts:
            previous_page += "".join([f"&concept={concept}" for concept in concepts])
        response["previousPage"] = previous_page

    return response
