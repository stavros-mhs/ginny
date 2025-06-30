from src.core.solve.workflow import iterate, execute
from src.utils.tools.read_pdf_tool import ReadPDFTool
from langchain_community.tools import WriteFileTool


def run_solve(pdf_path, accuracy):
    program = iterate()
    result = execute(program, pdf_path, accuracy)
