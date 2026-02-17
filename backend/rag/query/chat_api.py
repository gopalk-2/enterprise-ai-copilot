from security.auth.dependencies import get_current_user
from fastapi import Depends
from fastapi import APIRouter
from pydantic import BaseModel
from .qa_chain import get_qa_chain
from agents.tool_calling.agent import get_tool_agent
from observability.audit_service import (
    log_query,
    log_response,
    log_error,
    measure_time
)
import time


router = APIRouter()
class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
def chat(request: QueryRequest,user=Depends(get_current_user)):
    start_time = time.time()
    try:
        log_query(user["sub"], request.query)
        role = user["role"]
        agent = get_tool_agent()

        try:
            agent_response = agent.run(request.query)
            if agent_response:
                log_response(user["sub"], agent_response)
                measure_time(start_time)
                return {"agent_response": agent_response}
        except Exception:
            pass

        qa_chain = get_qa_chain(role)
        response = qa_chain(request.query)

        log_response(user["sub"], response["result"])
        measure_time(start_time)

        return {
        "user": user["sub"],
        "role":role,
        "answer": response["result"],
        "sources": [
            doc.metadata for doc in response["source_documents"]
        ]
    }
    except Exception as e:
        log_error(user["sub"], str(e))
        raise
