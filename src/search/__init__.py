from abc import ABC, abstractmethod
from typing import Iterable, List, Optional

from rich.progress import track

from src.document import Document


class SearchEngine(ABC):
    @abstractmethod
    def add_document(self, document: Document):
        raise NotImplementedError

    def add_documents(
        self, documents: Iterable[Document], progress_bar: Optional[bool] = False
    ):
        if progress_bar:
            documents = track(documents, description="Indexing documents")

        for document in documents:
            self.add_document(document)

    @abstractmethod
    def search(self, search_terms: str, n: int) -> List[Document]:
        raise NotImplementedError

    @abstractmethod
    def get_document(self, id: str) -> Document:
        raise NotImplementedError
