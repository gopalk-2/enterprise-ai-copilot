"""
Supervisor Agent — Multi-Agent Orchestrator
Uses LangGraph to classify queries and delegate to specialized worker agents.
Workers: data_analyzer, support, code_review, general.
"""

from typing import TypedDict, Optional, List, Any
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent


# --- State Definition ---
class SupervisorState(TypedDict):
    query: str
    role: str
    assigned_agent: Optional[str]
    response: Optional[str]
    sources: Optional[list]
    ui_components: Optional[List[Any]]
    status_updates: Optional[List[str]]


# --- LLM ---
llm = ChatOllama(model="gemma4:31b-cloud", temperature=0.0)


# --- Supervisor Classifier ---
classifier_prompt = ChatPromptTemplate.from_template(
    """You are a Supervisor Agent for an Enterprise AI Assistant. Your job is to classify a query and delegate it to the most appropriate specialist worker agent.

Available worker agents:
1. 'data_analyzer' — For queries about metrics, analytics, revenue, statistics, charts, dashboards, data visualization, subscriptions, headcount, or any numerical analysis.
2. 'support' — For queries about company policies, HR questions, SLAs, support tickets, internal knowledge base lookups, benefits, travel, expenses, or compliance.
3. 'code_review' — For queries about code quality, architecture guidelines, tech stack, engineering best practices, deployment processes, or code review requests.
4. 'general' — For general actions like sending emails, generating summaries, triggering workflows, fetching subscription details, or any action that doesn't fit the above categories.

Respond with ONLY the exact agent name in lowercase (data_analyzer, support, code_review, or general). No other text.

USER QUERY: {query}
AGENT:"""
)

classifier_chain = classifier_prompt | llm | StrOutputParser()


def classify_query(state: SupervisorState):
    """Supervisor node: classify the query and pick a worker."""
    query = state["query"]
    result = classifier_chain.invoke({"query": query}).strip().lower()
    
    # Normalize the output
    if "data" in result or "analy" in result:
        agent = "data_analyzer"
    elif "support" in result:
        agent = "support"
    elif "code" in result or "review" in result:
        agent = "code_review"
    else:
        agent = "general"
    
    return {
        "assigned_agent": agent,
        "status_updates": [f"Delegating to {agent} agent..."]
    }


# --- Worker Execution Nodes ---

def execute_data_analyzer(state: SupervisorState):
    """Execute the Data Analyzer worker agent."""
    from agents.workers.data_analyzer import get_data_analyzer_tools
    
    tools = get_data_analyzer_tools()
    agent = create_react_agent(llm, tools=tools)
    
    try:
        result = agent.invoke({"messages": [("user", state["query"])]})
        response = str(result["messages"][-1].content)
        
        # Extract chart/table data directly from tool call outputs (not LLM prose)
        ui_components = _extract_ui_from_tool_messages(result.get("messages", []))
        
        return {
            "response": response,
            "sources": [],
            "ui_components": ui_components,
            "status_updates": (state.get("status_updates") or []) + ["Data analysis complete."]
        }
    except Exception as e:
        print(f"Data Analyzer agent error: {e}")
        return {
            "response": f"I encountered an error while analyzing the data: {str(e)}",
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + [f"Error in data analysis."]
        }


def execute_support(state: SupervisorState):
    """Execute the Support worker agent."""
    from agents.workers.support_agent import get_support_tools
    
    tools = get_support_tools()
    agent = create_react_agent(llm, tools=tools)
    
    try:
        result = agent.invoke({"messages": [("user", state["query"])]})
        response = str(result["messages"][-1].content)
        return {
            "response": response,
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + ["Support query resolved."]
        }
    except Exception as e:
        print(f"Support agent error: {e}")
        return {
            "response": f"I encountered an error processing your support request: {str(e)}",
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + ["Error in support agent."]
        }


def execute_code_review(state: SupervisorState):
    """Execute the Code Review worker agent."""
    from agents.workers.code_review_agent import get_code_review_tools
    
    tools = get_code_review_tools()
    agent = create_react_agent(llm, tools=tools)
    
    try:
        result = agent.invoke({"messages": [("user", state["query"])]})
        response = str(result["messages"][-1].content)
        return {
            "response": response,
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + ["Code review complete."]
        }
    except Exception as e:
        print(f"Code Review agent error: {e}")
        return {
            "response": f"I encountered an error with the code review: {str(e)}",
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + ["Error in code review."]
        }


def execute_general(state: SupervisorState):
    """Execute the General worker agent (backward compatible with original tool agent)."""
    from agents.workers.general_agent import get_general_tools
    
    tools = get_general_tools()
    agent = create_react_agent(llm, tools=tools)
    
    try:
        result = agent.invoke({"messages": [("user", state["query"])]})
        response = str(result["messages"][-1].content)
        return {
            "response": response,
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + ["Action completed."]
        }
    except Exception as e:
        print(f"General agent error: {e}")
        return {
            "response": f"I encountered an error while executing that action: {str(e)}",
            "sources": [],
            "ui_components": [],
            "status_updates": (state.get("status_updates") or []) + ["Error in general agent."]
        }


# --- Routing Logic ---

def route_to_worker(state: SupervisorState):
    """Route to the assigned worker based on the supervisor's classification."""
    return state["assigned_agent"]


# --- Helper: Extract UI Components from Tool Messages ---

def _extract_ui_from_tool_messages(messages: list) -> list:
    """Extract chart/table data directly from ToolMessage outputs in the agent's message history.
    This is far more reliable than regex-parsing the LLM's final prose answer."""
    import json
    from langchain_core.messages import ToolMessage

    components = []
    
    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue
        
        content = msg.content
        if not content or not isinstance(content, str):
            continue
        
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            continue
        
        # Chart data (from generate_chart_data tool)
        if isinstance(data, dict) and "chart_type" in data:
            components.append({
                "component": "chart",
                "data": data
            })
        # Table data (from query_database tool)
        elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            components.append({
                "component": "table",
                "data": data
            })
    
    return components


# --- Build the Supervisor Graph ---

supervisor_graph = StateGraph(SupervisorState)

# Add nodes
supervisor_graph.add_node("classify", classify_query)
supervisor_graph.add_node("data_analyzer", execute_data_analyzer)
supervisor_graph.add_node("support", execute_support)
supervisor_graph.add_node("code_review", execute_code_review)
supervisor_graph.add_node("general", execute_general)

# Add edges
supervisor_graph.add_edge(START, "classify")

supervisor_graph.add_conditional_edges(
    "classify",
    route_to_worker,
    {
        "data_analyzer": "data_analyzer",
        "support": "support",
        "code_review": "code_review",
        "general": "general"
    }
)

supervisor_graph.add_edge("data_analyzer", END)
supervisor_graph.add_edge("support", END)
supervisor_graph.add_edge("code_review", END)
supervisor_graph.add_edge("general", END)

# Compile
compiled_supervisor = supervisor_graph.compile()
