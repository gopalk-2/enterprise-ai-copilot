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
from utils.query_classifier import is_greeting
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

    try:

        # 1️⃣ Log incoming query
        log_query(username, query)

        # 2️⃣ Greeting Shortcut (skip AI pipeline)
        if is_greeting(query):
            response_text = "Hello! How can I help you today?"

            add_message(username, "user", query)
            add_message(username, "assistant", response_text)

            log_response(username, response_text)
            measure_time(start_time)

            return {"answer": response_text}

        # 3️⃣ Retrieve conversation history
        history = get_conversation(username)

        # 4️⃣ Build contextual conversation for RAG
        contextual_query = ""

        for msg in history:
            contextual_query += f"{msg['role']}: {msg['content']}\n"

        contextual_query += f"user: {query}"

        # 5️⃣ Try Agent Tool Execution
        agent = get_tool_agent()

        try:
            # Agent should only get the user query
            agent_response = agent.run(query)

            if agent_response:
                add_message(username, "user", query)
                add_message(username, "assistant", agent_response)

                log_response(username, agent_response)
                measure_time(start_time)

                return {"agent_response": agent_response}

        except Exception:
            # If agent fails → fallback to RAG
            pass

        # 6️⃣ RAG Knowledge Retrieval
        qa_chain = get_qa_chain(role)

        response = qa_chain(contextual_query)

        answer = response["result"]

        # 7️⃣ Update memory
        add_message(username, "user", query)
        add_message(username, "assistant", answer)

        # 8️⃣ Audit logging
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

        # System error logging
        log_error(username, str(e))
        raise