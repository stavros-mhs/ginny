import platform

# from subprocess import run
from langchain_community.document_loaders import PyPDFLoader
from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class PdfInput (BaseModel):
    """Path to .pdf document"""

    path: str = Field(description=f"Absolute path for a pdf file stored in a {platform.system()} system.")
    
    # reason: str = Field(description="One-sentence reason (up to 140 chars) for running the command.")
    # not obvious to me if this ^^^^ will better the execution

class PdfTool (BaseTool):
    name: str = "PdfTool"
    description: str = "Used to load a pdf from the given path."
    args_schema: Type[BaseModel] = PdfInput

    def _run (self, path: str) -> str:
        print (f"loading {path}.")

        payload = PyPDFLoader (path)
        document = payload.load () # why not lazy_load () or load_and_split ()

        pdf_text = [doc.page_content for doc in document]

        result = {"pages": pdf_text}

        return str(result)

