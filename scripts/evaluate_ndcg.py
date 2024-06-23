"""
Use a set of relevance judgements to evaluate search engine performance using NDCG.

The relevance judgements are generated using the generate_relevance_judgements.py
script, and are loaded from the data/eval/relevance/judgements.json file. This file
contains a dictionary of search terms and relevance scores for a plausible set of search
terms that a user might use to find documents in the corpus.

The search engine is evaluated using the NDCG metric, which compares the ranking of the
search engine in question with the ideal ranking of the search engine, according to the
relevance scores. The NDCG@k metric is computed for k=5 and k=10, and the results are
printed to the console.
"""

import json
from pathlib import Path

from elasticsearch import Elasticsearch
from rich import box, console, progress, table

from src.document import Document
from src.evaluation.ndcg import NDCG
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

console.print(
    f"📚 Loaded {sum([len(group) for group in judgements.values()])} "
    f"relevance judgements across {len(judgements)} search terms"
)

# evaluate the search engine against the gold-standard relevance judgements
table = table.Table(box=box.ROUNDED)
table.add_column("Search terms", justify="left")
table.add_column("k=5", justify="center")
table.add_column("k=10", justify="center")

scores_at_5 = []
scores_at_10 = []
for search_terms, relevance_scores in judgements.items():
    search_response = search_engine.search(search_terms=search_terms, page_size=10)
    search_results = search_response.results
    ndcg = NDCG(
        relevance_scores=relevance_scores,
        search_result_ids=[doc.id for doc in search_results],
    )

    ndcg_at_5 = ndcg.compute(5)
    scores_at_5.append(ndcg_at_5)

    ndcg_at_10 = ndcg.compute(10)
    scores_at_10.append(ndcg_at_10)

    table.add_row(search_terms, f"{ndcg_at_5:.2f}", f"{ndcg_at_10:.2f}")

# add a footer with the overall NDCG scores
table.add_row(
    "Overall",
    f"{sum(scores_at_5) / len(scores_at_5):.2f}",
    f"{sum(scores_at_10) / len(scores_at_10):.2f}",
)

console.print(table)
