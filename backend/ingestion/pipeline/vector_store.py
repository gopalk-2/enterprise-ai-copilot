import os
from langchain_chroma import Chroma
current_dir = os.path.dirname(os.path.abspath(__file__))
ABS_PERSIST_DIR = os.path.join(current_dir, "../../data/embeddings")
def store_embeddings(chunks, embeddings):
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=ABS_PERSIST_DIR
    )

    return vectordb
