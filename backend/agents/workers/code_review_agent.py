from langchain.tools import tool


@tool
def review_code_snippet(code: str) -> str:
    """Review a code snippet for best practices, potential bugs, and suggest improvements."""
    issues = []
    suggestions = []
    
    if "password" in code.lower() and ("=" in code or "==" in code):
        issues.append("⚠️ Potential hardcoded password detected. Use environment variables or a secrets manager.")
    
    if "eval(" in code or "exec(" in code:
        issues.append("🚨 Use of eval()/exec() detected. This is a security vulnerability — avoid dynamic code execution.")
    
    if "import *" in code:
        issues.append("⚠️ Wildcard import detected. Use explicit imports for clarity and to avoid namespace pollution.")
    
    if "try:" in code and "except:" in code and "Exception" not in code:
        issues.append("⚠️ Bare except clause detected. Always catch specific exceptions.")
    
    if "print(" in code:
        suggestions.append("💡 Consider using the `logging` module instead of print() for production code.")
    
    if "TODO" in code or "FIXME" in code:
        suggestions.append("📝 Found TODO/FIXME comments. Consider creating tickets to track these.")
    
    if not issues and not suggestions:
        return "✅ Code looks clean! No major issues found. Follow the Engineering Architecture Guidelines for deployment."
    
    result = "## Code Review Results\n\n"
    if issues:
        result += "### Issues Found\n" + "\n".join(f"- {i}" for i in issues) + "\n\n"
    if suggestions:
        result += "### Suggestions\n" + "\n".join(f"- {s}" for s in suggestions) + "\n"
    
    return result


@tool
def search_engineering_docs(topic: str) -> str:
    """Search engineering architecture guidelines and best practices documentation."""
    from rag.query.qa_chain import get_qa_chain
    
    enriched_query = f"engineering architecture guidelines for {topic}"
    qa_chain = get_qa_chain(role="employee")
    result = qa_chain(enriched_query)
    answer = result.get("result", "No engineering documentation found.")
    sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]
    return f"{answer}\n\nSources: {', '.join(sources)}"


@tool
def check_tech_stack_compliance(technology: str) -> str:
    """Check if a given technology is compliant with the company's approved tech stack."""
    import json
    
    approved_stack = {
        "backend": ["Python", "FastAPI", "Go", "Gin"],
        "frontend": ["React", "Next.js", "TypeScript"],
        "databases": ["PostgreSQL", "Redis", "ChromaDB", "Neo4j"],
        "infrastructure": ["Kubernetes", "EKS", "Terraform", "Docker"],
        "monitoring": ["Datadog", "OpenTelemetry", "Prometheus"],
        "ci_cd": ["GitHub Actions"],
        "llm": ["Ollama", "Mistral", "BAAI/bge-small-en"]
    }
    
    tech_lower = technology.lower()
    for category, techs in approved_stack.items():
        for t in techs:
            if tech_lower in t.lower():
                return json.dumps({
                    "technology": technology,
                    "status": "APPROVED ✅",
                    "category": category,
                    "notes": f"{technology} is part of the approved {category} stack."
                }, indent=2)
    
    return json.dumps({
        "technology": technology,
        "status": "NOT IN APPROVED STACK ⚠️",
        "action_required": "Submit a Technology Approval Request (TAR) to the Architecture Review Board.",
        "approved_alternatives": approved_stack
    }, indent=2)


def get_code_review_tools():
    """Return all code review agent tools."""
    return [review_code_snippet, search_engineering_docs, check_tech_stack_compliance]
