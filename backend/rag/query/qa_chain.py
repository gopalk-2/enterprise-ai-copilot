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


# ──────────────────────────────────────────────────────────────────────────────
# NORMAL QA CHAIN  (Semantic Cache → HyDE → Hybrid Retrieval → LLM)
# ──────────────────────────────────────────────────────────────────────────────
def get_qa_chain(role):

    llm = OllamaLLM(model="gemma4:31b-cloud", temperature=0.0)
    retriever = get_retriever(role)

    def qa_chain(query):
        from cache.semantic_cache import semantic_cache
        from observability.audit_service import log_cache_hit, log_cache_miss

        # ── 1. Semantic cache check ──────────────────────────────────────────
        cached = semantic_cache.get(query)
        if cached:
            log_cache_hit("system", query)
            return {
                "result": cached["answer"],
                "source_documents": [],
                "cache_hit": True,
            }

        log_cache_miss("system", query)

        # ── 2. HyDE: Generate Hypothetical Document ──────────────────────────
        formatted_hyde_prompt = hyde_prompt.format(question=query)
        hypothetical_doc = llm.invoke(formatted_hyde_prompt)

        # Combine the original query with the hallucinated document
        search_query = f"{query}\n\n{hypothetical_doc}"

        # ── 3. Retrieve ───────────────────────────────────────────────────────
        docs = retriever.invoke(search_query)

        # ── 4. Rerank ─────────────────────────────────────────────────────────
        reranked_docs = rerank(query, docs)
        top_docs = reranked_docs[:3]
        vector_context = "\n\n".join([doc.page_content for doc in top_docs])

        # ── 5. Graph enrichment (optional) ────────────────────────────────────
        graph_context = ""
        try:
            from rag.knowledge_graph.graph_retriever import retrieve_from_graph
            graph_context = retrieve_from_graph(query)
        except Exception:
            pass

        context = vector_context
        if graph_context:
            context += f"\n\n--- Entity Relationships ---\n{graph_context}"

        # ── 6. LLM answer ─────────────────────────────────────────────────────
        formatted_prompt = prompt.format(context=context, question=query)
        answer = llm.invoke(formatted_prompt)

        # ── 7. Populate cache ─────────────────────────────────────────────────
        semantic_cache.set(query, answer, [doc.metadata for doc in top_docs])

        return {
            "result": answer,
            "source_documents": top_docs,
            "cache_hit": False,
        }

    return qa_chain


# ──────────────────────────────────────────────────────────────────────────────
# STREAMING QA FUNCTION  (Semantic Cache → HyDE → Hybrid Retrieval → LLM stream)
# ──────────────────────────────────────────────────────────────────────────────
def stream_answer(role, query):
    from cache.semantic_cache import semantic_cache
    from observability.audit_service import log_cache_hit, log_cache_miss

    # ── 1. Semantic cache check ──────────────────────────────────────────────
    cached = semantic_cache.get(query)
    if cached:
        log_cache_hit("system", query)

        def cached_generator():
            """Yield cached answer character-by-character to mimic streaming."""
            for char in cached["answer"]:
                yield char

        return cached_generator(), [], True   # (generator, source_docs, cache_hit)

    log_cache_miss("system", query)

    llm = OllamaLLM(model="gemma4:31b-cloud", temperature=0.0)
    retriever = get_retriever(role)

    # ── 2. HyDE ───────────────────────────────────────────────────────────────
    formatted_hyde_prompt = hyde_prompt.format(question=query)
    hypothetical_doc = llm.invoke(formatted_hyde_prompt)
    search_query = f"{query}\n\n{hypothetical_doc}"

    # ── 3. Retrieve + Rerank ──────────────────────────────────────────────────
    docs = retriever.invoke(search_query)
    reranked_docs = rerank(query, docs)
    top_docs = reranked_docs[:3]
    vector_context = "\n\n".join([doc.page_content for doc in top_docs])

    # ── 4. Graph enrichment ───────────────────────────────────────────────────
    graph_context = ""
    try:
        from rag.knowledge_graph.graph_retriever import retrieve_from_graph
        graph_context = retrieve_from_graph(query)
    except Exception:
        pass

    context = vector_context
    if graph_context:
        context += f"\n\n--- Entity Relationships ---\n{graph_context}"

    formatted_prompt = prompt.format(context=context, question=query)
    stream = llm.stream(formatted_prompt)

    # Accumulate full answer so we can populate the cache after streaming
    accumulated: list[str] = []

    def streaming_generator():
        for chunk in stream:
            token = chunk if isinstance(chunk, str) else str(chunk)
            accumulated.append(token)
            yield token
        # ── 5. Populate cache once the stream is exhausted ────────────────────
        full_answer = "".join(accumulated)
        semantic_cache.set(query, full_answer, [doc.metadata for doc in top_docs])

    return streaming_generator(), top_docs, False   # (generator, source_docs, cache_hit)