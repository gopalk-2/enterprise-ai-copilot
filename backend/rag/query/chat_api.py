from security.auth.dependencies import get_current_user
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from .qa_chain import get_qa_chain
from agents.tool_calling.agent import get_tool_agent
from utils.query_router import route_query
from observability.audit_service import (
    log_query,
    log_response,
    log_error,
    measure_time
)
from memory.sqlite_memory  import (
    add_message,
    get_recent_conversation,
    get_conversation
)
from memory.context_summarizer import summarize_conversation
import time

router = APIRouter()

class QueryRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(request: QueryRequest, user=Depends(get_current_user)):
    start_time = time.time()
    username = user["sub"]
    role = user["role"]
    query = request.query
    
    # New Routing Logic
    route = route_query(query)

    try:
        # 1️⃣ Log incoming query
        log_query(username, query)
        
        # 2️⃣ Length Check (Global Safety)
        if len(query) > 1000:
            return {"answer": "Your query is too long. Please shorten it."}

        # 3️⃣ Retrieve conversation history (For RAG or Agent context)
        history = get_conversation(username)
        summary = summarize_conversation(history)
        recent_messages = get_recent_conversation(username)
        contextual_query = ""
        if summary:
             contextual_query += f"Conversation summary: {summary}\n\n"
        for msg in recent_messages:
             contextual_query += f"{msg['role']}: {msg['content']}\n"

        contextual_query += f"user: {query}"

        # --- ROUTING LOGIC START ---

        # CASE A: GREETING
        if route == "greeting":
            response_text = "Hello! How can I help you today?"
            add_message(username, "user", query)
            add_message(username, "assistant", response_text)
            log_response(username, response_text)
            measure_time(start_time)
            return {"answer": response_text}

        # CASE B: AGENT
        elif route == "agent":
            agent = get_tool_agent()
            try:
                # Agents usually handle their own memory, so we pass the raw query
                agent_response = agent.run(query)
                if agent_response:
                    add_message(username, "user", query)
                    add_message(username, "assistant", agent_response)
                    log_response(username, agent_response)
                    measure_time(start_time)
                    return {"agent_response": agent_response}
            except Exception as e:
                # If agent fails, we fall through to RAG as a backup
                print(f"Agent failed: {e}")
                pass 

        # CASE C: RAG (Default or explicit)
        # Note: We use 'query' for retrieval to fix your "missing document" bug
        # but you can pass 'contextual_query' to the chain for LLM context.
        qa_chain = get_qa_chain(role)
        
        # IMPORTANT: If your qa_chain logic performs retrieval, 
        # passing the raw 'query' is more likely to find the document.
        response = qa_chain(query) 
        answer = response["result"]

        # 7️⃣ Update memory & Log
        add_message(username, "user", query)
        add_message(username, "assistant", answer)
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
        log_error(username, str(e))
        raise