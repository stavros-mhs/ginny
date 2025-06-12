from langchain_core.tools import tool
from langchain_core.messages import SystemMessage


@tool
def ReadParsedPDF(config: dict) -> dict:
    """appends parsed_pdf from state to message history"""

    print("hello from ReadParsedPDF")

    parsed_pdf = config["parsed_pdf"]
    pdf_to_str = "\n\n".join(parsed_pdf["pages"])
    print("ReadParsedPDF", pdf_to_str)

    return {"messages": [SystemMessage(content=pdf_to_str)]}
