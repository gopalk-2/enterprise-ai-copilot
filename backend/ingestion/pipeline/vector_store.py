from langchain_chroma import Chroma


def store_embeddings(chunks, embeddings):
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="../../data/embeddings"
    )

    return vectordb
