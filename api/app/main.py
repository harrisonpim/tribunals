from fastapi import FastAPI

from app.routers import concepts, documents

app = FastAPI()


app.include_router(concepts.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    return {"status": "ok"}
