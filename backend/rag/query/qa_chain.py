from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from .retriever import get_retriever
from .reranker import rerank

# Shared prompt template — updated to handle both vector and graph context
template = """
ROLE: You are an expert Enterprise AI Assistant.

INSTRUCTIONS:
1. Answer the question comprehensively using ONLY the provided Context.
2. Structure your response BEAUTIFULLY using Markdown. Use clear headings (## or ###), standard bullet points (`-`), and **bold text** to make it incredibly readable, just like ChatGPT would. If listing items, ALWAYS prefix them with `- `.
3. For EVERY factual claim you make, you MUST cite the source using the exact Markdown link format: `[Source Name](#source)` at the end of the sentence. Example: `The remote work policy requires VPN [HR-Policy.pdf](#source).`
4. If multiple sources support a point, list them directly: `[File A](#source) [File B](#source)`.
5. If the context includes Entity Relationships from a knowledge graph, use that information to explain connections between departments, policies, people, and tools.
6. If the answer is not in the context, clearly state that you don't have the internal documentation to answer.
7. Speak in a helpful, concise, and professional tone.

CONTEXT:
{context}

QUESTION:
{question}

COMPREHENSIVE MARKDOWN ANSWER WITH CITATIONS:
"""

prompt = ChatPromptTemplate.from_template(template)


# HyDE Prompt Template
hyde_template = """
You are an expert Enterprise AI Assistant. 
Please write a short, highly plausible hypothetical document or passage that would perfectly answer the following question. 
Do not include any pleasantries or conversational text, just the hypothetical document content.

QUESTION:
{question}

HYPOTHETICAL DOCUMENT:
"""
hyde_prompt = ChatPromptTemplate.from_template(hyde_template)


# ---------------------------------------
# NORMAL QA CHAIN (with Hybrid Retrieval)
# ---------------------------------------
def get_qa_chain(role):

    llm = OllamaLLM(model="mistral", temperature=0.0)

    retriever = get_retriever(role)

    def qa_chain(query):
        
        # 1. HyDE: Generate Hypothetical Document
        formatted_hyde_prompt = hyde_prompt.format(question=query)
        hypothetical_doc = llm.invoke(formatted_hyde_prompt)
        
        # Combine the original query with the hallucinated document for maximum semantic overlap
        search_query = f"{query}\n\n{hypothetical_doc}"

        # 2. Retrieve using the enriched query (Vector)
        docs = retriever.invoke(search_query)

        # 3. Rerank using the original query against the retrieved docs
        reranked_docs = rerank(query, docs)

        top_docs = reranked_docs[:3]

        vector_context = "\n\n".join([doc.page_content for doc in top_docs])

        # 4. Graph retrieval (optional enrichment)
        graph_context = ""
        try:
            from rag.knowledge_graph.graph_retriever import retrieve_from_graph
            graph_context = retrieve_from_graph(query)
        except Exception:
            pass  # Graph not available, continue with vector-only

        # 5. Combine contexts
        context = vector_context
        if graph_context:
            context += f"\n\n--- Entity Relationships ---\n{graph_context}"

        formatted_prompt = prompt.format(
            context=context,
            question=query
        )

        answer = llm.invoke(formatted_prompt)

        return {
            "result": answer,
            "source_documents": top_docs
        }

    return qa_chain


# ---------------------------------------
# STREAMING QA FUNCTION (with Hybrid Retrieval)
# ---------------------------------------
def stream_answer(role, query):

    llm = OllamaLLM(model="mistral", temperature=0.0)

    retriever = get_retriever(role)

    # 1. HyDE: Generate Hypothetical Document
    formatted_hyde_prompt = hyde_prompt.format(question=query)
    hypothetical_doc = llm.invoke(formatted_hyde_prompt)
    
    # Combine the original query with the hallucinated document
    search_query = f"{query}\n\n{hypothetical_doc}"

    # 2. Retrieve using the enriched query
    docs = retriever.invoke(search_query)

    # 3. Rerank using the original query
    reranked_docs = rerank(query, docs)

    top_docs = reranked_docs[:3]

    vector_context = "\n\n".join([doc.page_content for doc in top_docs])

    # 4. Graph retrieval (optional enrichment)
    graph_context = ""
    try:
        from rag.knowledge_graph.graph_retriever import retrieve_from_graph
        graph_context = retrieve_from_graph(query)
    except Exception:
        pass

    # 5. Combine contexts
    context = vector_context
    if graph_context:
        context += f"\n\n--- Entity Relationships ---\n{graph_context}"

    formatted_prompt = prompt.format(
        context=context,
        question=query
    )

    stream = llm.stream(formatted_prompt)

    def string_generator():
        for chunk in stream:
            yield chunk if isinstance(chunk, str) else str(chunk)

    return string_generator(), top_docs