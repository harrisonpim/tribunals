"""
Use the Claude API to generate domain-specific relevance judgements for tribunal docs.

Based loosely on "Large language models can accurately predict searcher preferences"
https://arxiv.org/abs/2309.10621

We use NDCG@k as our gold-standard metric for evaluating the performance of the search
engine. NDCG is based on comparing the ranking of the search engine with the ideal
ranking of the search engine according to a set of relevance scores. These are usually
manually generated by human judges, but recent work has shown that large language models
can be used to generate relevance scores that are well-correlated with human judgements.

We use a naive, unoptimised query to retrieve the top 1000 documents from the
corpus for a set of known search terms. We then use the Claude API to generate relevance
scores for these documents. We can then use these relevance scores to evaluate the
performance of the search engine when developing new ranking algorithms.
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from elasticsearch import Elasticsearch
from rich.console import Console
from rich.progress import track

from src.document import Document

console = Console()

with open("data/raw/search_terms.json") as f:
    search_terms = json.load(f)[:10]

with console.status("Setting up directories..."):
    data_dir = Path("data")
    relevance_eval_dir = data_dir / "eval" / "relevance"
    relevance_eval_dir.mkdir(parents=True, exist_ok=True)
console.print("📁 Set up data directories", style="green")


with console.status("Setting up Elasticsearch index..."):
    es = Elasticsearch(
        hosts=[{"host": "localhost", "port": 9200, "scheme": "http"}],
        request_timeout=30,
        max_retries=10,
        retry_on_timeout=True,
    )
    index_name = "naive"
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(
        index=index_name,
        settings={
            "analysis": {
                "analyzer": {
                    "naive": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip"],
                        "filter": ["lowercase", "asciifolding"],
                    }
                }
            }
        },
        mappings={"properties": {"text": {"type": "text", "analyzer": "naive"}}},
    )
console.print(f"🚧 Set up Elasticsearch index: {index_name}", style="green")

documents_dir = data_dir / "processed" / "documents"
for doc in track(
    list(documents_dir.glob("*.json")),
    description="Indexing documents...",
    console=console,
    transient=True,
):
    with doc.open() as f:
        data = json.load(f)
    text = data["title"] + " " + data["text"]
    es.index(index="naive", document={"text": text}, id=doc.stem)
console.print("🤓 Indexed documents", style="green")

candidate_docs_dict = {}
for term in track(
    search_terms, "Retrieving candidate documents...", console=console, transient=True
):
    res = es.search(index="naive", query={"match": {"text": term}}, size=1000)
    candidate_docs_dict[term] = [hit["_id"] for hit in res["hits"]["hits"]]
console.print("🔍 Retrieved candidate documents for eval search terms", style="green")

with open(relevance_eval_dir / "candidate_docs.json", "w") as f:
    json.dump(candidate_docs_dict, f)
console.print(f"💾 Saved candidate document IDs to {relevance_eval_dir}", style="green")

es.indices.delete(index=index_name)
console.print(f"🧹 Deleted Elasticsearch index: {index_name}", style="green")

system_prompt = """
You are a search quality rater, with the task of evaluating the relevance of documents in a corpus which pertains to UK employment tribunal decisions.
You will been given a set of search terms and a set of documents from the corpus which may be relevant to those search terms.
Given a query and a document, you must provide a score on an integer scale of 0 to 2 with the following meanings:

2 = highly relevant, very helpful for this query
1 = relevant, may be partly helpful but might contain other irrelevant content
0 = not relevant, should never be shown for this query

Assume that you are writing a report on the subject of the topic. If you would use any of the information contained in the document in such a report, mark it 1. If the document is primarily about the topic, or contains vital information about the topic, mark it 2. Otherwise, mark it 0.

You will be paid $0.10 for each document you score, so don't miss any documents!
You will be paid a bonus of $0.10 for each document you score correctly, so please take your time and be accurate in your judgements.

Answer with a JSON array of scores, without providing any reasoning, equivocation, or commentary. For example, your response should look like this:
[{ "document_id": "abcdefg", "relevance": 2 }, { "document_id": "hijklmn", "relevance": 1 }, { "document_id": "opqrstu", "relevance": 0 }]
"""  # noqa: E501

prompt_template = """
SEARCH TERMS:
A person has typed "{{search_term}}" into a search engine. They are looking for information about UK employment tribunal decisions.

CANIDATE DOCUMENTS:

{{candidates}}

INSTRUCTIONS:
1. For each document, read the title and summary.
2. Decide if the document is relevant to the search term.
3. Assign a score of 0, 1, or 2 to each document.
4. Submit your scores as a JSON array.

RESPONSE:
"""  # noqa: E501


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
judgements = {}
for term in track(
    search_terms, "Generating relevance judgements...", console=console, transient=True
):
    candidate_docs = [
        Document.load(data_dir / "processed" / "documents" / f"{document_id}.json")
        for document_id in candidate_docs_dict[term]
    ]
    # batch the documents to avoid making the prompt too long
    document_batches = [
        candidate_docs[i : i + 10] for i in range(0, len(candidate_docs), 10)
    ]

    judgements[term] = {}

    for batch in document_batches:
        display_docs = [
            {"id": doc.id, "title": doc.title, "summary": doc.summary} for doc in batch
        ]

        prompt = prompt_template.replace("{{search_term}}", term).replace(
            "{{candidates}}", json.dumps(display_docs)
        )

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ],
        )
        response = message.content[0].text
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            print("Error decoding response")
            print(response)
            continue

        for doc in response:
            judgements[term][doc["document_id"]] = doc["relevance"]

        with open(relevance_eval_dir / "judgements.json", "w") as f:
            json.dump(judgements, f, indent=4)

console.print(f"💾 Saved relevance judgements to {relevance_eval_dir}", style="green")

# Print some rough summary statistics about the relevance judgements
judgements = [
    relevance for term in judgements for relevance in judgements[term].values()
]
console.print(f"📊 Number of judgements: {len(judgements)}")
console.print(f"📊 Number of irrelevant documents: {judgements.count(0)}")
console.print(f"📊 Number of highly relevant documents: {judgements.count(2)}")
