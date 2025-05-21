from langchain_community.tools import ReadFileTool, WriteFileTool
from src.core.implementation_node.implementer import iterate, execute


def run_impl (goal):
    toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    program = iterate (toolbox)
    result = execute (program, goal)
    print (result)