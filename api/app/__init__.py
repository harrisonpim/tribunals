import os
from typing import Optional, Sequence, Union

from elasticsearch import Elasticsearch
from fastapi import Request
from pydantic import BaseModel, Field

from src.concept import Concept
from src.document import Document

default_page_size = 10
elasticsearch_instance = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


class APIResponse(BaseModel):
    totalResults: int = Field(
        ...,
        description=(
            "The total number of results, including those not returned on the "
            "current page"
        ),
    )
    nextPage: Optional[str] = Field(
        None, description="The URL for the next page of results"
    )
    previousPage: Optional[str] = Field(
        None, description="The URL for the previous page of results"
    )
    results: Sequence[Union[Document, Concept]] = Field(
        ..., description="The results for the current page"
    )


def get_base_url(request: Request) -> str:
    return request.url.scheme + "://" + request.url.netloc + request.url.path


def get_next_page_url(base_url: str, page: int, page_size: int, **kwargs) -> str:
    kwargs["page"] = page + 1
    if page_size != default_page_size:
        kwargs["pageSize"] = page_size
    for key, value in list(kwargs.items()):
        if isinstance(value, list):
            kwargs[key] = ",".join(value)
    return base_url + "?" + "&".join(f"{k}={v}" for k, v in kwargs.items() if v)


def get_previous_page_url(base_url: str, page: int, page_size: int, **kwargs) -> str:
    kwargs["page"] = page - 1
    if page_size != default_page_size:
        kwargs["pageSize"] = page_size
    for key, value in list(kwargs.items()):
        if isinstance(value, list):
            kwargs[key] = ",".join(value)
    return base_url + "?" + "&".join(f"{k}={v}" for k, v in kwargs.items() if v)
