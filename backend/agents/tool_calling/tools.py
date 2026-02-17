from langchain.tools import tool

@tool
def generate_summary(text: str):
    """Generate a summary of provided text."""
    return f"Summary: {text[:150]}"


@tool
def send_email(to: str, subject: str, body: str):
    """Send an email to recipient."""
    return f"Email prepared for {to} with subject '{subject}'"
