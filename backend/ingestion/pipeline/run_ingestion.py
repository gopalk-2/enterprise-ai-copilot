from document_loader import load_documents
from text_splitter import get_splitters
from embedder import get_embedding_model
from vector_store import get_parent_document_retriever
from langchain_core.documents import Document

def run_pipeline():
    print("Loading documents...")
    raw_docs = load_documents()
    print(f"DEBUG: Loaded {len(raw_docs)} raw documents")

    docs = [Document(page_content=d["text"], metadata=d["metadata"]) for d in raw_docs]

    print("Initializing splitters...")
    parent_splitter, child_splitter = get_splitters()

    print("Generating embeddings...")
    embeddings = get_embedding_model()

    print("Initializing ParentDocumentRetriever...")
    retriever = get_parent_document_retriever(embeddings, parent_splitter, child_splitter)

    print("Storing in vector DB & local storage...")
    retriever.add_documents(docs)

    print("Done!")


if __name__ == "__main__":
    run_pipeline()
