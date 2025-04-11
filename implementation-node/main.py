import sys

from langchain_community.tools import ReadFileTool, WriteFileTool
from .implementer import iterate, execute

if __name__ == "__main__":

    user_in = sys.argv [1]

    toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    program = iterate (toolbox)
    result = execute (program, user_in)
    print (result)