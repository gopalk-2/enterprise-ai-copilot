import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Calculate the absolute path relative to THIS file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to reach 'backend', then into 'data/embeddings'
PERSIST_DIR = os.path.join(current_dir, "../../data/embeddings")

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en"
)
def get_retriever(role="employee"):
    vectordb = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embedding_model
    )

    return vectordb.as_retriever(
        search_kwargs={
            "k": 6,
            "filter": {"access_role": role}
        }
    )
