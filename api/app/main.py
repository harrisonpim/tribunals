from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import concepts, documents, elasticsearch_instance

app = FastAPI(
    title="Employment Appeal Tribunals API",
    version="0.1.0",
    description="API for querying employment appeal tribunal decisions",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(concepts.router)
app.include_router(documents.router)


@app.get("/health-check")
async def health_check() -> dict:
    if not elasticsearch_instance.ping():
        raise HTTPException(status_code=503, detail="Service unavailable")

    missing_indices = [
        index
        for index in ["concepts", "documents"]
        if not elasticsearch_instance.indices.exists(index=index)
    ]

    if missing_indices:
        # Log the error internally, but don't expose it to the client
        print(f"Error: missing indices {missing_indices}")
        raise HTTPException(status_code=503, detail="Service unavailable")

    return {"status": "ok"}
