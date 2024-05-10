import os

from elasticsearch import Elasticsearch
from fastapi import FastAPI, HTTPException

from . import concepts, documents

app = FastAPI(
    title="Employment Appeal Tribunals API",
    version="0.1.0",
    description="API for querying employment appeal tribunal decisions",
    docs_url="/",
)


app.include_router(concepts.router)
app.include_router(documents.router)

es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "localhost:9200")],
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


@app.get("/health-check")
async def health_check() -> dict:
    if not es.ping():
        raise HTTPException(status_code=503, detail="Service unavailable")

    missing_indices = [
        index
        for index in ["concepts", "documents"]
        if not es.indices.exists(index=index)
    ]

    if missing_indices:
        # Log the error internally, but don't expose it to the client
        print(f"Error: missing indices {missing_indices}")
        raise HTTPException(status_code=503, detail="Service unavailable")

    return {"status": "ok"}
