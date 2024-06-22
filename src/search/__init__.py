from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Union

from pydantic import BaseModel
from rich.progress import track

from src.concept import Concept
from src.document import Document

Item = Union[Concept, Document]


class SearchResponse(BaseModel):
    total: int
    results: List[Item]


class SearchEngine(ABC):
    @abstractmethod
    def insert_item(self, item: Item):
        raise NotImplementedError

    def insert_items(self, items: Iterable[Item], progress_bar: Optional[bool] = False):
        if progress_bar:
            items = track(items, description="Indexing items")
        for item in items:
            self.insert_item(item)

    @abstractmethod
    def search(
        self, search_terms: str, page: int = 1, page_size: int = 10
    ) -> SearchResponse:
        raise NotImplementedError

    @abstractmethod
    def get_item(self, id: str) -> Item:
        raise NotImplementedError
