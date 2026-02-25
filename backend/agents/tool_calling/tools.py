from integrations.connectors.db_connector import get_user_subscriptions
from integrations.connectors.workflow_connector import trigger_workflow
from langchain.tools import tool

@tool
def generate_summary(text: str):
    """Generate a summary of provided text."""
    return f"Summary: {text[:150]}"


@tool
def send_email(to: str, subject: str, body: str):
    """Send an email to recipient."""
    return f"Email prepared for {to} with subject '{subject}'"


@tool
def fetch_subscriptions(user_id: int):
    """Fetch active subscriptions for user"""
    return str(get_user_subscriptions(user_id))


@tool
def start_approval_workflow(name: str):
    """Trigger approval workflow"""
    return trigger_workflow(name, {"initiated_by": "AI"})
