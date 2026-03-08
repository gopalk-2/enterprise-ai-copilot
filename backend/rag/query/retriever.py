import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import LocalFileStore, create_kv_docstore
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Calculate the absolute path relative to THIS file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to reach 'backend', then into 'data/embeddings'
PERSIST_DIR = os.path.join(current_dir, "../../data/embeddings")
STORE_DIR = os.path.join(current_dir, "../../data/parent_docs")

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en"
)

def get_retriever(role="employee"):
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embedding_model
    )
    
    fs = LocalFileStore(STORE_DIR)
    store = create_kv_docstore(fs)

    # Pydantic requires TextSplitter instances even if only executing retrieval
    dummy_parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    dummy_child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=dummy_child_splitter,
        parent_splitter=dummy_parent_splitter,
        search_kwargs={
            "k": 6,
            "filter": {"access_role": role}
        }
    )

    return retriever
