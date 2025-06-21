from langchain_community.document_loaders import PyPDFLoader

def pdftostr (pdf_path: str) -> dict:
    payload = PyPDFLoader (pdf_path)
    document = payload.load ()

    return "".join (doc.page_content for doc in document)
