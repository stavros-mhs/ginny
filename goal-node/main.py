import sys

from langchain_community.tools import ReadFileTool, WriteFileTool
from goal_spotter import iterate, execute

from pdf_to_json import pdftojson

if __name__ == "__main__":

    user_in = sys.argv [1]

    make_json = pdftojson (user_in)

    toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    program = iterate (toolbox)
    result = execute (program, make_json)
    
    with open("summary.txt", "w") as f:
        f.write (result)