import os
import fitz  # PyMuPDF
from docx import Document

DATA_PATH = "/Users/gopalkumar/Desktop/enterprise-ai-assistant/data/documents"


def load_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text


def load_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_documents():
    docs = []

    for file in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, file)

        if file.endswith(".pdf"):
            docs.append(load_pdf(path))

        elif file.endswith(".docx"):
            docs.append(load_docx(path))

        elif file.endswith(".txt"):
            docs.append(load_txt(path))

    return docs
