from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from .retriever import get_retriever
from .reranker import rerank

def get_qa_chain(role):

    # Keep temperature at 0.0 for factual accuracy
    llm = Ollama(model="mistral", temperature=0.0)
    template = """
    ROLE: Professional Enterprise Assistant.

    INSTRUCTIONS:
    1. Answer the question using ONLY the provided Context.
    2. For every factual claim you make, you MUST cite the source at the end of the sentence like this: [Source: Filename].
    3. If multiple sources support a point, list them: [Source: FileA, FileB].
    4. If the answer is not in the context, say you don't have the internal documentation.
    5. Be concise and professional.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    FACTUAL ANSWER WITH CITATIONS:
    """

    prompt = ChatPromptTemplate.from_template(template)

    retriever = get_retriever(role)

    def qa_chain(query):

        # 1️⃣ Retrieve documents
        docs = retriever.invoke(query)

        # 2️⃣ Re-rank documents
        reranked_docs = rerank(query, docs)

        # 3️⃣ Select top documents
        top_docs = reranked_docs[:3]

        # 4️⃣ Build context
        context = "\n\n".join([doc.page_content for doc in top_docs])

        # 5️⃣ Format prompt
        formatted_prompt = prompt.format(
            context=context,
            question=query
        )

        # 6️⃣ Call LLM
        answer = llm.invoke(formatted_prompt)

        return {
            "result": answer,
            "source_documents": top_docs
        }

    return qa_chain