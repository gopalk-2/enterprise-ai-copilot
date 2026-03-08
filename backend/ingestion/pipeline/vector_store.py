import os
from langchain_chroma import Chroma
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import LocalFileStore, create_kv_docstore

current_dir = os.path.dirname(os.path.abspath(__file__))
ABS_PERSIST_DIR = os.path.join(current_dir, "../../data/embeddings")
ABS_STORE_DIR = os.path.join(current_dir, "../../data/parent_docs")

def get_parent_document_retriever(embeddings, parent_splitter, child_splitter):
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        persist_directory=ABS_PERSIST_DIR, 
        embedding_function=embeddings
    )
    
    # The storage layer for the parent documents (must handle Document serialization)
    fs = LocalFileStore(ABS_STORE_DIR)
    store = create_kv_docstore(fs)
    
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    return retriever
