import subprocess
import shlex

from src.utils.state import AgentState
from src.utils.pretty_print import beautify

# COMPILATION STEP
def compilation_wrapper(state: AgentState):
    compiler = state ["compiler_choice"]
    flags = state ["flags"]
    source_file_name = state ["source_file_name"]
    binary_file_name = state ["binary_file_name"]

    compilation_cmd = compiler + " " + flags + " " + source_file_name + " " + "-o" + " " + binary_file_name
    print (f"compiling using: {compilation_cmd}")
    cmd_to_list = shlex.split (compilation_cmd)

    res = subprocess.run (cmd_to_list, capture_output=True, text=True)

    exit_code = res.returncode
    stderr = res.stderr.strip () 

    compilation_out = (
        f"compilation finished with exit code: {exit_code}\nstderr: {stderr}\n"
    )

    return {**state, "exit_code": exit_code, "compilation_out": compilation_out}


def pass_compilation(state: AgentState):
    exit_code = state["exit_code"]
    if not exit_code:
        beautify ("COMPILATION SUCCESSFUL")
        return "continue"
    else:
        beautify ("COMPILATION FAILED")
        return "retry"