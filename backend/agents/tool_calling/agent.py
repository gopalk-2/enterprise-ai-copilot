from langchain.agents import create_agent
from langchain_ollama import OllamaLLM
from .tools import generate_summary, send_email,fetch_subscriptions,start_approval_workflow

def get_tool_agent():
    llm = OllamaLLM(model="mistral")

    tools = [
        generate_summary,
        send_email,
        fetch_subscriptions,
        start_approval_workflow
    ]

    # Create a React-style agent (replacement for ZERO_SHOT_REACT_DESCRIPTION)
    agent = create_agent(
        model=llm,
        tools=tools
    )

    return agent
