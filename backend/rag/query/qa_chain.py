from langchain_community.llms import Ollama 
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from .retriever import get_retriever

def get_qa_chain(role):
    # Keep temperature at 0.0 for factual accuracy
    llm = Ollama(model="mistral", temperature=0.0) 

    # Revised template with Citation instructions
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

    FACTUAL ANSWER WITH CITATIONS:"""

    prompt = ChatPromptTemplate.from_template(template)
    
    retriever = get_retriever(role)

    # We ensure the chain returns the source documents so the backend can see them
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True, 
        chain_type_kwargs={"prompt": prompt}
    )