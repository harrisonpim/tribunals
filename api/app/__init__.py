from typing import List, Union

from src.concept import Concept
from src.document import Document

default_page_size = 10


def format_response_metadata(
    res: dict,
    base_url: str,
    page: int,
    pageSize: int,
    query: str,
    results: Union[List[Document], List[Concept]],
):
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
