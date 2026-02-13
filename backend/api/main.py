from fastapi import FastAPI
from rag.query.chat_api import router as chat_router

app = FastAPI(title="Enterprise AI Assistant")

app.include_router(chat_router)

@app.get("/")
def root():
    return {"status": "running"}
