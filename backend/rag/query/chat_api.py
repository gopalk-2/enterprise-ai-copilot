import json
import time
from security.auth.dependencies import get_current_user
from security.guardrails import run_guardrails
from fastapi import Depends, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .qa_chain import get_qa_chain, stream_answer
from agents.router_graph import app_graph, semantic_router
from observability.audit_service import (
    log_query,
    log_response,
    log_error,
    log_cache_hit,
    log_cache_miss,
    measure_time,
    log_route,
)
from memory.sqlite_memory import (
    add_message,
    get_recent_conversation,
    get_conversation,
)
from memory.context_summarizer import summarize_conversation

router = APIRouter()

# Minimum chars for a response to be promoted to a markdown artifact
ARTIFACT_MIN_CHARS = 600


class QueryRequest(BaseModel):
    query: str


def _ndjson_line(data: dict) -> str:
    """Format a dict as a newline-delimited JSON line."""
    return json.dumps(data) + "\n"


def _should_be_artifact(text: str) -> bool:
    """
    Heuristic: promote a RAG answer to a markdown artifact when it is
    - long (≥ ARTIFACT_MIN_CHARS characters), AND
    - structured (contains at least one markdown heading  ## or ###)
    """
    return len(text) >= ARTIFACT_MIN_CHARS and ("##" in text or "###" in text)


def _infer_artifact_title(query: str) -> str:
    """Generate a concise artifact title from the original query."""
    words = query.strip().rstrip("?").split()
    title = " ".join(words[:8])
    return title.capitalize() if title else "AI Response"


@router.post("/chat")
def chat(request: QueryRequest, user=Depends(get_current_user)):
    start_time = time.time()
    username = user["sub"]
    role = user["role"]
    query = request.query

    try:
        log_query(username, query)

        # ── Guardrail pre-filter ──────────────────────────────────────────────
        guard = run_guardrails(query, user=username)
        if guard.blocked:
            return {
                "user":   username,
                "role":   role,
                "route":  "blocked",
                "answer": f"⛔ Request blocked: {guard.block_reason}",
                "sources": [],
                "blocked": True,
            }
        query = guard.safe_query   # use PII-redacted version

        if len(query) > 1000:
            return {"answer": "Your query is too long. Please shorten it."}

        history = get_conversation(username)
        summary = summarize_conversation(history)
        recent_messages = get_recent_conversation(username)
        contextual_query = ""
        if summary:
            contextual_query += f"Conversation summary: {summary}\n\n"
        for msg in recent_messages:
            contextual_query += f"{msg['role']}: {msg['content']}\n"
        contextual_query += f"user: {query}"

        result = app_graph.invoke({"query": query, "role": role})
        route = result.get("route", "rag")
        answer = result.get("response", "No response generated.")
        sources = result.get("sources", [])
        ui_components = result.get("ui_components", [])
        cache_hit = result.get("cache_hit", False)

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
            "ui_components": ui_components,
            "cache_hit": cache_hit,
        }

    except Exception as e:
        log_error(username, str(e))
        raise


@router.post("/chat/stream")
def chat_stream(request: QueryRequest, user=Depends(get_current_user)):
    """
    NDJSON streaming endpoint.
    Each line is a JSON object with a 'type' field:
      - {"type": "status",       "content": "..."}
      - {"type": "cache_status", "content": "...", "hit": bool}
      - {"type": "token",        "content": "..."}
      - {"type": "sources",      "content": [...]}
      - {"type": "ui_component", "component": "chart", "data": {...}}
      - {"type": "artifact",     "artifact_type": "markdown"|"code"|"mermaid",
                                  "title": "...", "content": "...", "language": "..."}
      - {"type": "done"}
    """
    username = user["sub"]
    role = user["role"]
    query = request.query

    # ── Guardrail pre-filter (runs before routing) ────────────────────────────
    guard = run_guardrails(query, user=username)
    if guard.blocked:
        def blocked_stream():
            yield _ndjson_line({
                "type":    "status",
                "content": f"⛔ Request blocked by security filter: {guard.block_reason}",
            })
            yield _ndjson_line({"type": "done"})
        return StreamingResponse(blocked_stream(), media_type="application/x-ndjson")
    query = guard.safe_query   # use PII-redacted version

    route_state = semantic_router({"query": query, "role": role})
    route = route_state.get("route", "rag")

    try:
        log_query(username, query)

        # ── Greeting ─────────────────────────────────────────────────────────
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

        # ── Agent (Multi-Agent Supervisor) ────────────────────────────────────
        if route == "agent":
            def agent_stream():
                yield _ndjson_line({"type": "status", "content": "Routing to specialist agent..."})
                agent_response = "Failed to execute agent action."
                try:
                    result = app_graph.invoke({"query": query, "role": role})
                    agent_response = result.get("response", "Failed to execute agent action.")
                    ui_components = result.get("ui_components", [])
                    status_updates = result.get("status_updates", [])
                    artifact_data = result.get("artifact", None)

                    for status in status_updates:
                        yield _ndjson_line({"type": "status", "content": status})

                    for char in agent_response:
                        yield _ndjson_line({"type": "token", "content": char})

                    for comp in ui_components:
                        yield _ndjson_line({
                            "type": "ui_component",
                            "component": comp.get("component", "unknown"),
                            "data": comp.get("data", {}),
                        })

                    # Emit artifact if agent provided one
                    if artifact_data:
                        yield _ndjson_line({"type": "artifact", **artifact_data})
                    elif _should_be_artifact(agent_response):
                        yield _ndjson_line({
                            "type": "artifact",
                            "artifact_type": "markdown",
                            "title": _infer_artifact_title(query),
                            "content": agent_response,
                        })

                    add_message(username, "user", query)
                    add_message(username, "assistant", agent_response)
                    log_response(username, agent_response)
                except Exception as e:
                    log_error(username, f"Agent stream error: {e}")
                    yield _ndjson_line({"type": "status", "content": " Error executing agent."})
                finally:
                    yield _ndjson_line({"type": "done"})
            return StreamingResponse(agent_stream(), media_type="application/x-ndjson")

        # ── RAG Streaming (with Semantic Cache + Artifact promotion) ──────────
        def rag_stream():
            yield _ndjson_line({"type": "status", "content": "Searching knowledge base..."})
            full_answer = ""

            try:
                answer_stream, source_docs, cache_hit = stream_answer(role, query)

                if cache_hit:
                    log_cache_hit(username, query)
                    yield _ndjson_line({
                        "type": "cache_status",
                        "content": "⚡ Answered from semantic cache",
                        "hit": True,
                    })
                else:
                    log_cache_miss(username, query)
                    yield _ndjson_line({
                        "type": "cache_status",
                        "content": "🔍 Running full retrieval pipeline",
                        "hit": False,
                    })

                for token in answer_stream:
                    full_answer += token
                    yield _ndjson_line({"type": "token", "content": token})

                sources = [doc.metadata for doc in source_docs]
                yield _ndjson_line({"type": "sources", "content": sources})

                # Promote to artifact when the answer is a long structured document
                if _should_be_artifact(full_answer):
                    yield _ndjson_line({
                        "type": "artifact",
                        "artifact_type": "markdown",
                        "title": _infer_artifact_title(query),
                        "content": full_answer,
                    })

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