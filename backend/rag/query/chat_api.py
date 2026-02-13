from fastapi import APIRouter
from pydantic import BaseModel
from .qa_chain import get_qa_chain

router = APIRouter()

qa_chain = get_qa_chain()


class QueryRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(request: QueryRequest):
    response = qa_chain(request.query)

    return {
        "answer": response["result"],
        "sources": [
            doc.metadata for doc in response["source_documents"]
        ]
    }
