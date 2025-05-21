import sys
import json

from langchain_community.tools import ReadFileTool, WriteFileTool
from src.core.goal_node.goal_spotter import iterate, execute

from src.utils.pdf_to_json import pdftojson

if __name__ == "__main__":

    user_in = sys.argv [1]

    make_json = pdftojson (user_in)

    toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    program = iterate (toolbox)
    result = execute (program, json.dumps(make_json, indent=2, ensure_ascii=False))
    
    with open("summary.txt", "w") as f:
        f.write (result)