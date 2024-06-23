"""
Index documents and concepts into an elasticsearch cluster.

This script loads documents and concepts from the data/processed directory and indexes
them into an elasticsearch cluster. The elasticsearch cluster is assumed to be running
locally on the default port (9200).
"""

from pathlib import Path

from elasticsearch import Elasticsearch
from rich.console import Console
from rich.progress import track

from src.concept import Concept
from src.document import Document
from src.search.core import ConceptSearchEngine, DocumentSearchEngine

console = Console()

es = Elasticsearch(
    hosts=[{"host": "localhost", "port": 9200, "scheme": "http"}],
    request_timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)

# load documents and index them
documents_dir = Path("data/processed/documents")
files = list(documents_dir.glob("*.json"))
documents = [
    Document.load(file, parse_sentences=False)
    for file in track(
        files, description="Loading documents", console=console, transient=True
    )
]
console.print(f"📄 Loaded {len(documents)} documents")

document_search_engine = DocumentSearchEngine(elasticsearch=es, index_name="documents")
document_search_engine.insert_items(items=documents, progress_bar=True)
console.print(f"🚚 Indexed {len(documents)} documents")


# load concepts and index them
concepts_dir = Path("data/processed/concepts")
files = list(concepts_dir.glob("*.json"))
concepts = [
    Concept.load(file)
    for file in track(
        files, description="Loading concepts", console=console, transient=True
    )
]
console.print(f"🧠 Loaded {len(concepts)} concepts")

concept_search_engine = ConceptSearchEngine(elasticsearch=es, index_name="concepts")
concept_search_engine.insert_items(items=concepts, progress_bar=True)
console.print(f"🚚 Indexed {len(concepts)} concepts")

console.print("✅ Indexing complete")
