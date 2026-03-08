# New
from langchain_text_splitters import RecursiveCharacterTextSplitter # pyright: ignore[reportMissingImports]

def get_splitters():
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    return parent_splitter, child_splitter
