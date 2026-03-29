from langchain.tools import tool
from rag.query.qa_chain import get_qa_chain


@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal enterprise knowledge base for policy information, guidelines, and documentation."""
    qa_chain = get_qa_chain(role="employee")
    result = qa_chain(query)
    answer = result.get("result", "No information found.")
    sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]
    return f"{answer}\n\nSources: {', '.join(sources)}"


@tool
def create_ticket(title: str, description: str, priority: str = "medium") -> str:
    """Create a support ticket in the internal ticketing system. Priority can be: low, medium, high, critical."""
    import json
    ticket = {
        "ticket_id": "TKT-2026-04217",
        "title": title,
        "description": description,
        "priority": priority.upper(),
        "status": "OPEN",
        "assigned_to": "Support Team",
        "created_at": "2026-03-28T15:00:00Z",
        "sla_response_by": "2026-03-28T19:00:00Z" if priority.lower() == "high" else "2026-03-29T15:00:00Z"
    }
    return json.dumps(ticket, indent=2)


@tool
def check_sla_status(severity_level: str) -> str:
    """Check the SLA requirements and current compliance status for a given severity level (1-4)."""
    import json
    sla_data = {
        "1": {
            "severity": "Critical (Sev 1)",
            "initial_response": "15 minutes",
            "resolution_target": "4 hours",
            "escalation_path": "VP Engineering (4h) → CEO (8h)",
            "current_compliance": "98.2%",
            "open_incidents": 0
        },
        "2": {
            "severity": "High (Sev 2)",
            "initial_response": "1 hour",
            "resolution_target": "8 hours",
            "escalation_path": "Engineering Manager (8h)",
            "current_compliance": "95.4%",
            "open_incidents": 2
        },
        "3": {
            "severity": "Medium (Sev 3)",
            "initial_response": "4 hours",
            "resolution_target": "24 hours",
            "escalation_path": "Team Lead",
            "current_compliance": "97.1%",
            "open_incidents": 8
        },
        "4": {
            "severity": "Low (Sev 4)",
            "initial_response": "24 hours",
            "resolution_target": "5 business days",
            "escalation_path": "N/A",
            "current_compliance": "99.5%",
            "open_incidents": 15
        }
    }
    
    level = severity_level.strip().replace("Sev ", "").replace("sev ", "")
    data = sla_data.get(level)
    if data:
        return json.dumps(data, indent=2)
    return json.dumps({"error": f"Unknown severity level: {severity_level}. Valid levels: 1, 2, 3, 4"})


def get_support_tools():
    """Return all support agent tools."""
    return [search_knowledge_base, create_ticket, check_sla_status]
