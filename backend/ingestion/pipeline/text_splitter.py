# New
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter # pyright: ignore[reportMissingImports]


def split_text(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )
    docs = [Document(page_content=d["text"], metadata=d["metadata"]) for d in documents]

    return splitter.split_documents(docs)
