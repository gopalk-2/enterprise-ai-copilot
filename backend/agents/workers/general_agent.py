from agents.tool_calling.tools import (
    generate_summary,
    send_email,
    fetch_subscriptions,
    start_approval_workflow
)


def get_general_tools():
    """Return all general-purpose agent tools (migrated from the original tool agent)."""
    return [generate_summary, send_email, fetch_subscriptions, start_approval_workflow]
