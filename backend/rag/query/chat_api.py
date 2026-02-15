from security.auth.dependencies import get_current_user
from fastapi import Depends
from fastapi import APIRouter
from pydantic import BaseModel
from .qa_chain import get_qa_chain

router = APIRouter()
class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
def chat(request: QueryRequest,user=Depends(get_current_user)):
    role=user["role"]
    qa_chain=get_qa_chain(role)
    response = qa_chain(request.query)
    return {
        "user": user["sub"],
        "role":role,
        "answer": response["result"],
        "sources": [
            doc.metadata for doc in response["source_documents"]
        ]
    }
