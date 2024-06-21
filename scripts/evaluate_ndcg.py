import json
from pathlib import Path

from elasticsearch import Elasticsearch
from rich import box, console, progress, table

from src.document import Document
from src.search.core import DocumentSearchEngine

console = console.Console()

data_dir = Path("data/processed")
document_dir = data_dir / "documents"
document_files = list(document_dir.glob("*.json"))
documents = [
    Document.load(file, parse_sentences=False)
    for file in progress.track(
        document_files, description="Loading documents", transient=True
    )
]
console.print(f"📄 Loaded {len(documents)} documents")

# create an elasticsearch instance for the search engine
es = Elasticsearch(hosts=[{"host": "localhost", "port": 9200, "scheme": "http"}])

# create a search engine instance and populate it with documents
index_name = "documents"
search_engine = DocumentSearchEngine(elasticsearch=es, index_name="documents")
console.print(f"🚚 Indexing documents in '{index_name}'")
if not search_engine.elasticsearch.indices.exists(index=index_name):
    search_engine.add_documents(documents=documents, progress_bar=True)

# load the relevance judgements
with open("data/eval/relevance/judgements.json", "r") as f:
    judgements = json.load(f)
n_judgements = sum([len(group) for group in judgements.values()])
console.print(f"📚 Loaded {n_judgements} relevance judgements")

# run an example query
search_terms = "covid 19"
console.print(f"🔍 Searching for '{search_terms}'")
results = search_engine.search(search_terms, n=10)
console.print(f"🫡 Found {len(results)} results")

# create a rich table to display the search results
table = table.Table(box=box.ROUNDED, show_lines=True)
table.add_column("ID", justify="right")
table.add_column("Summary")
for result in results:
    table.add_row(str(result.id), str(result.summary).strip())

console.print(table)
