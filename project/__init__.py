import sys

from project.tools.bashtool import BashTool
from langchain_community.tools import ReadFileTool

from .blocks import while_loop, execute
from project.tools.pdfloadertool import PdfTool
from project.tools.gcctool import GccTool
from project.tools.customwritetool import WriteFileTool

def main():
    """Simple neurosymbolic solver with bash/read/write file capabilities."""
    if len(sys.argv) < 2:
        print("Usage: You need to provide an instruction to the neurosymbolic solver.")
        sys.exit(1)

    user_input = sys.argv[1]

    toolbox = [BashTool(), ReadFileTool(verbose=True), WriteFileTool(verbose=True), PdfTool (), GccTool ()]
    program = while_loop(toolbox)
    result = execute(program, user_input)
    print(result)


__all__ = ["main"]