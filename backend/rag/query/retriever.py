import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Calculate the absolute path relative to THIS file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to reach 'backend', then into 'data/embeddings'
PERSIST_DIR = os.path.join(current_dir, "../../data/embeddings")


def get_retriever():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    return vectordb.as_retriever(search_kwargs={"k": 3})
