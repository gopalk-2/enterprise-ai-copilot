"""
Hybrid Retriever — Combines Vector RAG + Graph RAG
Merges context from the Chroma vector store and Neo4j knowledge graph
to provide richer, relationship-aware answers.
"""

from rag.query.retriever import get_retriever
from rag.knowledge_graph.graph_retriever import retrieve_from_graph
from rag.knowledge_graph.graph_store import is_available as is_graph_available


def hybrid_retrieve(query: str, role: str = "employee") -> tuple:
    """
    Retrieve context from both vector store and knowledge graph.
    
    Returns:
        tuple: (combined_context_string, list_of_source_documents)
    """
    # 1. Vector retrieval (always available)
    vector_retriever = get_retriever(role)
    vector_docs = vector_retriever.invoke(query)
    
    vector_context = "\n\n".join([doc.page_content for doc in vector_docs])
    
    # 2. Graph retrieval (optional, graceful fallback)
    graph_context = ""
    if is_graph_available():
        graph_context = retrieve_from_graph(query)
    
    # 3. Combine contexts
    combined_context = vector_context
    if graph_context:
        combined_context += f"\n\n--- Entity Relationships ---\n{graph_context}"
    
    return combined_context, vector_docs
