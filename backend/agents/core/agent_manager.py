from .tools import generate_summary, send_email_stub
from rag.query.qa_chain import get_qa_chain

class AgentManager:
    def __init__(self, role: str):
        """
        Initialize the manager once. 
        Pre-loading the chain prevents lag on every message.
        """
        self.role = role
        # Initialize the chain once during startup
        self.qa_chain = get_qa_chain(role)

    def run_agent(self, query: str) -> str:
        """
        Main execution logic for the assistant.
        """
        if not query or not query.strip():
            return "How can I help you today?"

        clean_query = query.strip()
        query_lower = clean_query.lower()

        # 1. High-Speed Greeting Guardrail
        # Using a set for O(1) lookup speed
        greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "greetings"}
        if query_lower in greetings:
            return "Hello! I am your Enterprise Assistant. How can I help you today?"

        # 2. Tool-Based Logic
        if "summary" in query_lower:
            return generate_summary(clean_query)

        if "email" in query_lower:
            return send_email_stub(
                "team@company.com",
                "AI Generated Content",
                clean_query
            )

        # 3. RAG Execution
        # RetrievalQA with return_source_documents=True returns a dictionary
        try:
            response = self.qa_chain({"query": clean_query})
            
            # Extract the 'result' key which contains Mistral's formatted answer
            answer = response.get("result")
            
            if not answer:
                return "I'm sorry, I couldn't generate an answer based on the available data."
                
            return answer

        except Exception:
            # Basic fallback for production stability
            return "I apologize, I'm having trouble accessing my database right now. Please try again."