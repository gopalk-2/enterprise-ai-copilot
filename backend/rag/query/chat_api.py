import json
import time
from security.auth.dependencies import get_current_user
from fastapi import Depends, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .qa_chain import get_qa_chain, stream_answer
from agents.router_graph import app_graph, semantic_router
from observability.audit_service import (
    log_query,
    log_response,
    log_error,
    measure_time
)
from memory.sqlite_memory import (
    add_message,
    get_recent_conversation,
    get_conversation
)
from memory.context_summarizer import summarize_conversation

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


def _ndjson_line(data: dict) -> str:
    """Format a dict as a newline-delimited JSON line."""
    return json.dumps(data) + "\n"


@router.post("/chat")
def chat(request: QueryRequest, user=Depends(get_current_user)):
    start_time = time.time()
    username = user["sub"]
    role = user["role"]
    query = request.query

    try:
        # 1. Log incoming query
        log_query(username, query)

        # 2. Length Check
        if len(query) > 1000:
            return {"answer": "Your query is too long. Please shorten it."}

        # 3. Retrieve conversation history
        history = get_conversation(username)
        summary = summarize_conversation(history)
        recent_messages = get_recent_conversation(username)
        contextual_query = ""
        if summary:
            contextual_query += f"Conversation summary: {summary}\n\n"
        for msg in recent_messages:
            contextual_query += f"{msg['role']}: {msg['content']}\n"
        contextual_query += f"user: {query}"

        # 4. Invoke the LangGraph orchestrator
        result = app_graph.invoke({"query": query, "role": role})
        route = result.get("route", "rag")
        answer = result.get("response", "No response generated.")
        sources = result.get("sources", [])
        ui_components = result.get("ui_components", [])

        # 5. Update memory & Log
        add_message(username, "user", query)
        add_message(username, "assistant", answer)
        log_response(username, answer)
        measure_time(start_time)

        return {
            "user": username,
            "role": role,
            "route": route,
            "answer": answer,
            "sources": sources,
            "ui_components": ui_components
        }

    except Exception as e:
        log_error(username, str(e))
        raise


@router.post("/chat/stream")
def chat_stream(request: QueryRequest, user=Depends(get_current_user)):
    """
    NDJSON streaming endpoint.
    Each line is a JSON object with a 'type' field:
      - {"type": "status", "content": "..."}     — Agent thinking/progress
      - {"type": "token", "content": "..."}       — Streamed text token
      - {"type": "sources", "content": [...]}     — Source citations
      - {"type": "ui_component", "component": "chart", "data": {...}} — Dynamic UI
      - {"type": "done"}                          — Stream complete
    """
    username = user["sub"]
    role = user["role"]
    query = request.query

    route_state = semantic_router({"query": query, "role": role})
    route = route_state.get("route", "rag")

    try:
        log_query(username, query)

        # --- Greeting ---
        if route == "greeting":
            def greeting_stream():
                yield _ndjson_line({"type": "status", "content": "Processing greeting..."})
                greeting = "Hello! 👋 How can I help you today? I can search our knowledge base, analyze data, review code, or help with support requests."
                yield _ndjson_line({"type": "token", "content": greeting})
                add_message(username, "user", query)
                add_message(username, "assistant", greeting)
                log_response(username, greeting)
                yield _ndjson_line({"type": "done"})

            return StreamingResponse(greeting_stream(), media_type="application/x-ndjson")

        # --- Agent (Multi-Agent Supervisor) ---
        if route == "agent":
            def agent_stream():
                yield _ndjson_line({"type": "status", "content": "Routing to specialist agent..."})

                agent_response = "Failed to execute agent action."
                try:
                    result = app_graph.invoke({"query": query, "role": role})
                    agent_response = result.get("response", "Failed to execute agent action.")
                    ui_components = result.get("ui_components", [])
                    status_updates = result.get("status_updates", [])

                    # Emit status updates from the supervisor
                    for status in status_updates:
                        yield _ndjson_line({"type": "status", "content": status})

                    # Stream the response token by token
                    for char in agent_response:
                        yield _ndjson_line({"type": "token", "content": char})

                    # Emit UI components
                    for comp in ui_components:
                        yield _ndjson_line({
                            "type": "ui_component",
                            "component": comp.get("component", "unknown"),
                            "data": comp.get("data", {})
                        })

                    # Save memory
                    add_message(username, "user", query)
                    add_message(username, "assistant", agent_response)
                    log_response(username, agent_response)
                except Exception as e:
                    log_error(username, f"Agent stream error: {e}")
                    yield _ndjson_line({"type": "status", "content": " Error executing agent."})
                finally:
                    yield _ndjson_line({"type": "done"})

            return StreamingResponse(agent_stream(), media_type="application/x-ndjson")

        # --- RAG Streaming ---
        def rag_stream():
            yield _ndjson_line({"type": "status", "content": "Searching knowledge base..."})

            full_answer = ""
            
            try:
                answer_stream, source_docs = stream_answer(role, query)
                for token in answer_stream:
                    full_answer += token
                    yield _ndjson_line({"type": "token", "content": token})

                # Emit sources
                sources = [doc.metadata for doc in source_docs]
                yield _ndjson_line({"type": "sources", "content": sources})
                
                # Save memory
                add_message(username, "user", query)
                add_message(username, "assistant", full_answer)
                log_response(username, full_answer)
            except Exception as e:
                log_error(username, f"RAG stream error: {e}")
                yield _ndjson_line({"type": "status", "content": " Error retrieving context."})
            finally:
                yield _ndjson_line({"type": "done"})

        return StreamingResponse(rag_stream(), media_type="application/x-ndjson")

    except Exception as e:
        log_error(username, str(e))
        raise