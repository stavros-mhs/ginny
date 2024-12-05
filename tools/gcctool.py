import platform

from subprocess import run
from langchain_community.document_loaders import PyPDFLoader
from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class GccInput(BaseModel):
    """Path to .c file"""

    path: str = Field(description=f"Absolute path for a pdf file stored in a {platform.system()} system.")
    
    # reason: str = Field(description="One-sentence reason (up to 140 chars) for running the command.")
    # not obvious to me if this ^^^^ will better the execution

class GccTool (BaseTool):
    name: str = "GccTool"
    description: str = "Used to compile a .c file."
    args_schema: Type[BaseModel] = GccInput

    def _run (self, path: str) -> str:
        print (f"compiling {path}.")

        process = run(["gcc", "-O0", "-m32", "-Wall", "-Wextra", "-Werror", "-pedantic", "-o", "main", path], capture_output=True)
        stdout = process.stdout.decode("utf-8")
        stderr = process.stderr.decode("utf-8")
        trunc_limit = 1024
        stdout_truncated = len(stdout) > trunc_limit
        stderr_truncated = len(stderr) > trunc_limit
        # timedout when it got killed by 9
        timeout = process.returncode == 137
        result = {
            "stdout": stdout[:trunc_limit],
            "stdout_truncated": stdout_truncated,
            "stderr": stderr[:trunc_limit],
            "stderr_truncated": stderr_truncated,
            "returncode": process.returncode,
            "timeout": timeout,
        }
        print(result)
        return str(result)

# TODO the current compilation command should be the "default", 
# TODO in case the user wants to use some other command formatting it should be allowed
