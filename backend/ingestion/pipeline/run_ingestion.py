from document_loader import load_documents
from text_splitter import split_text
from embedder import get_embedding_model
from vector_store import store_embeddings


def run_pipeline():
    print("Loading documents...")
    docs = load_documents()
    print(f"DEBUG: Loaded {len(docs)} raw documents")

    print("Splitting text...")
    chunks = split_text(docs)
    print(f"DEBUG: Created {len(chunks)} text chunks")

    print("Generating embeddings...")
    embeddings = get_embedding_model()

    print("Storing in vector DB...")
    store_embeddings(chunks, embeddings)

    print("Done!")


if __name__ == "__main__":
    run_pipeline()
