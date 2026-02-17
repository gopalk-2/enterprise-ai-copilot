from .agent_manager import AgentManager

agent = AgentManager()


def run_workflow(query):
    return agent.run_agent(query)
