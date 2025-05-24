from langchain_community.document_loaders import PyPDFLoader

def pdftojson (pdf_path: str) -> dict:
    payload = PyPDFLoader (pdf_path)
    document = payload.load ()

    pdf_text = [doc.page_content for doc in document]
    result = {"pages": pdf_text}

    return result
