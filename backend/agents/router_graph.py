"""
Router Graph — Main Orchestrator
Routes queries through a semantic router to: greeting, rag, or agent (supervisor).
The 'agent' route now delegates to the multi-agent Supervisor for specialized handling.
"""

from typing import TypedDict, Optional, List, Any
from langgraph.graph import StateGraph, START, END
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class RouterState(TypedDict):
    query: str
    role: str
    route: Optional[str]
    response: Optional[str]
    sources: Optional[list]
    ui_components: Optional[List[Any]]
    status_updates: Optional[List[str]]


# --- Semantic Router ---
router_prompt = ChatPromptTemplate.from_template(
    """You are a Semantic Router for an Enterprise AI Assistant.
Analyze the user's query and classify it into exactly ONE of the following three categories:

1. 'greeting': The user is just saying hi, hello, good morning, etc.
2. 'agent': The user is asking to perform an action, trigger a workflow, get a subscription, send an email, fetch data, analyze data, review code, check SLAs, create tickets, or do something active.
3. 'rag': The user is asking a question about company policies, rules, information, or general knowledge that requires searching the internal documentation.

Respond with ONLY the exact category name in lowercase (greeting, agent, or rag). Do not include any other text, punctuation, or explanation.

USER QUERY: {query}
CATEGORY:"""
)

llm = OllamaLLM(model="mistral", temperature=0.0)
router_chain = router_prompt | llm | StrOutputParser()


def semantic_router(state: RouterState):
    query = state["query"]
    route_result = router_chain.invoke({"query": query})

    # Clean up the output
    route = route_result.strip().lower()
    if "agent" in route:
        route = "agent"
    elif "greeting" in route:
        route = "greeting"
    else:
        route = "rag"

    return {
        "route": route,
        "status_updates": [f"Query classified as: {route}"]
    }


# --- Execution Nodes ---

from rag.query.qa_chain import get_qa_chain
from agents.supervisor import compiled_supervisor


def execute_rag(state: RouterState):
    query = state["query"]
    role = state["role"]
    
    status = (state.get("status_updates") or []) + ["Searching knowledge base..."]
    
    qa_chain = get_qa_chain(role)
    response = qa_chain(query)
    
    return {
        "response": response.get("result", ""),
        "sources": [doc.metadata for doc in response.get("source_documents", [])],
        "ui_components": [],
        "status_updates": status + ["Answer generated from internal documents."]
    }


def execute_agent(state: RouterState):
    """Delegate to the multi-agent Supervisor instead of a single tool agent."""
    query = state["query"]
    role = state["role"]
    
    status = (state.get("status_updates") or []) + ["Routing to specialist agent..."]
    
    try:
        result = compiled_supervisor.invoke({
            "query": query,
            "role": role
        })
        
        supervisor_statuses = result.get("status_updates", [])
        
        return {
            "response": result.get("response", "No response generated."),
            "sources": result.get("sources", []),
            "ui_components": result.get("ui_components", []),
            "status_updates": status + supervisor_statuses
        }
    except Exception as e:
        print(f"Supervisor agent failed: {e}")
        return {
            "response": "Sorry, I encountered an error while trying to execute that action.",
            "sources": [],
            "ui_components": [],
            "status_updates": status + [f"Error: {str(e)}"]
        }


def execute_greeting(state: RouterState):
    return {
        "response": "Hello! 👋 How can I help you today? I can search our knowledge base, analyze data, review code, or help with support requests.",
        "sources": [],
        "ui_components": [],
        "status_updates": ["Greeting handled."]
    }


def route_condition(state: RouterState):
    return state["route"]


# --- Build the Graph ---
workflow = StateGraph(RouterState)

workflow.add_node("semantic_router", semantic_router)
workflow.add_node("rag", execute_rag)
workflow.add_node("agent", execute_agent)
workflow.add_node("greeting", execute_greeting)

workflow.add_edge(START, "semantic_router")

workflow.add_conditional_edges(
    "semantic_router",
    route_condition,
    {
        "rag": "rag",
        "agent": "agent",
        "greeting": "greeting"
    }
)

workflow.add_edge("rag", END)
workflow.add_edge("agent", END)
workflow.add_edge("greeting", END)

# Compile the final graph
app_graph = workflow.compile()
