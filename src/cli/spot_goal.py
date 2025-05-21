import json

from src.core.goal_node.goal_spotter import iterate, execute
from src.utils.pdf_to_json import pdftojson

from langchain_community.tools import ReadFileTool, WriteFileTool

def run_goal (pdf_path):
    make_to_json = pdftojson (pdf_path)

    toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    program = iterate (toolbox)
    result = execute (program, json.dumps (make_to_json, indent=2, ensure_ascii=False))

    with open ("goal.txt", "w") as f:
        f.write (result)