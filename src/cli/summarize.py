import json

from langchain_community.tools import ReadFileTool, WriteFileTool
from src.core.summarize.summarizer import execute, iterate
from src.utils.pdf_to_str import pdftostr


def run_goal(pdf_path):
    make_to_str = pdftostr(pdf_path)
    toolbox = [ReadFileTool(verbose=True), WriteFileTool(verbose=True)]
    program = iterate(toolbox)
    result = execute(program, make_to_str)

    with open("summary.txt", "w") as f:
        f.write(result + "\n")
