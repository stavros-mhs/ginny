from langchain_community.document_loaders import PyPDFLoader


def pdftostr(pdf_path: str) -> str:
    payload = PyPDFLoader(pdf_path)
    document = payload.load()

    return "\n".join(doc.page_content for doc in document)
