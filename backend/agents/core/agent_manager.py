from .tools import generate_summary, send_email_stub


class AgentManager:

    def run_agent(self, query):
        if "summary" in query.lower():
            return generate_summary(query)

        if "email" in query.lower():
            return send_email_stub(
                "team@company.com",
                "AI Generated",
                query
            )

        return "No agent action triggered."
