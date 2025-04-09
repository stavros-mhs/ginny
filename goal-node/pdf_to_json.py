from langchain_community.document_loaders import PyPDFLoader
import json

def pdftojson (pdf_path: str) -> dict:
    payload = PyPDFLoader (pdf_path)
    document = payload.load () # why not lazy_load () or load_and_split ()

    pdf_text = [doc.page_content for doc in document]
    result = {"pages": pdf_text}

    json_out = json.dumps (result, ensure_ascii=False, indent=2)

    return json_out
