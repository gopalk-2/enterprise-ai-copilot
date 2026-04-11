"""
Graph Retriever — Natural Language to Cypher
Converts user queries into Cypher queries to retrieve relationship data from Neo4j.
Falls back gracefully to empty results if Neo4j is unavailable.
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from .graph_store import run_cypher, is_available

llm = OllamaLLM(model="gemma4:31b-cloud", temperature=0.0)

cypher_prompt = ChatPromptTemplate.from_template(
    """You are a Cypher query generator for a Neo4j knowledge graph about an enterprise.

The graph has these node types: Department, Policy, Person, Role, Product, Tool, Location, Process
The graph has these relationship types: OWNS, AUTHORED_BY, APPLIES_TO, USES, LOCATED_IN, REPORTS_TO, PART_OF, MANAGES

Given the user's question, generate a Cypher query to find the answer.
Return ONLY the Cypher query, no explanation.
If the question cannot be answered with a graph query, return: MATCH (n) RETURN n LIMIT 0

USER QUESTION: {query}
CYPHER QUERY:"""
)


def retrieve_from_graph(query: str) -> str:
    """Convert a natural language query to Cypher and retrieve graph context."""
    if not is_available():
        return ""
    
    try:
        # Generate Cypher query
        cypher = llm.invoke(cypher_prompt.format(query=query)).strip()
        
        # Clean up — remove any markdown formatting
        cypher = cypher.replace("```cypher", "").replace("```", "").strip()
        
        if not cypher or "LIMIT 0" in cypher:
            return ""
        
        # Execute the query
        results = run_cypher(cypher)
        
        if not results:
            return ""
        
        # Format results as context string
        context_parts = []
        for record in results[:10]:  # Limit to 10 results
            parts = []
            for key, value in record.items():
                if isinstance(value, dict):
                    # Node data
                    parts.append(f"{key}: {value.get('name', value)}")
                else:
                    parts.append(f"{key}: {value}")
            context_parts.append(" | ".join(parts))
        
        graph_context = "Knowledge Graph Results:\n" + "\n".join(context_parts)
        return graph_context
    
    except Exception as e:
        print(f"Graph retrieval error: {e}")
        return ""
