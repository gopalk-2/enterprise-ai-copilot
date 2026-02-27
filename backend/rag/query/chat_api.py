from security.auth.dependencies import get_current_user
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from .qa_chain import get_qa_chain
from agents.tool_calling.agent import get_tool_agent
from observability.audit_service import (
    log_query,
    log_response,
    log_error,
    measure_time
)
from memory.session_memory import (
    add_message,
    get_conversation
)
import time

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
def chat(request: QueryRequest, user=Depends(get_current_user)):
    start_time = time.time()
    username = user["sub"]
    role = user["role"]
    
    try:
        # 1. Audit: Log the incoming raw query
        log_query(username, request.query)

        # 2. Memory: Retrieve past conversation history
        history = get_conversation(username)

        # 3. Contextualization: Build the full conversation string
        # This allows the AI to understand follow-up questions
        contextual_query = ""
        for msg in history:
            contextual_query += f"{msg['role']}: {msg['content']}\n"
        
        contextual_query += f"user: {request.query}"

        # 4. Agent Execution: Attempt tool-calling with context
        agent = get_tool_agent()
        try:
            # Passing the full context so the agent can reference previous turns
            agent_response = agent.run(contextual_query)
            if agent_response:
                # Store the successful interaction in memory
                add_message(username, "user", request.query)
                add_message(username, "assistant", agent_response)
                
                log_response(username, agent_response)
                measure_time(start_time)
                return {"agent_response": agent_response}
        except Exception:
            # Fallback to standard RAG if the agent fails or isn't needed
            pass

        # 5. RAG Execution: Use QA Chain with the contextualized prompt
        qa_chain = get_qa_chain(role)
        response = qa_chain(contextual_query)
        answer = response["result"]

        # 6. Memory: Update history with the new exchange
        add_message(username, "user", request.query)
        add_message(username, "assistant", answer)

        # 7. Audit: Log final outcome and measure performance
        log_response(username, answer)
        measure_time(start_time)

        return {
            "user": username,
            "role": role,
            "answer": answer,
            "sources": [
                doc.metadata for doc in response.get("source_documents", [])
            ]
        }

    except Exception as e:
        # Log failure for system debugging
        log_error(username, str(e))
        raise