from langchain_community.llms import Ollama 
from langchain_classic.chains import RetrievalQA

from .retriever import get_retriever


def get_qa_chain():
    llm = Ollama(model="mistral")

    retriever = get_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain
