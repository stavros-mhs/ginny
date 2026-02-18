from typing import List

from pydantic import BaseModel, Field


class CompilationCMD(BaseModel):
    """String that represents a shell command to compile some source code to a binary executable"""

    compilation_cmd: List[str] = Field(
        ...,
        description="""
        A list of strings representing a full compilation command, tokenized as if you were to pass it into subprocess.run (),
        used to compile source code into a binary.
        
        Must include:
        - A compiler (e.g., gcc, g++, clang)
        - A source file (e.g., main.c, source.c)
        Can include:
        - Flags to (e.g., -Wall -Wextra -pedantic)
        - The `-o` flag, used to name the output binary (if -o is not used, the output binary is by default named a.out)

        Do NOT include markdown, comments, or explanations. Return only the list of shell arguments that constitue the compilation command. 
        """,
        examples=[
            ["gcc", "source.c"],
            ["gcc", "main.c", "-o", "mybin"],
            [
                "gcc",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-pedantic",
                "-o",
                "bin",
                "source.c",
            ],
        ],
    )


class TestCase(BaseModel):
    command: List[str] = Field(
        ...,
        description="""
        A list of shell arguments that form the test case command.

        Do NOT include markdown, comments, or explanations. Only the list of shell arguments that constitue the command. 
        """,
    )
    expected_out: str = Field(
        ...,
        description="""
        The expected output from running the command.

        Do NOT include markdown, comments, or explanations. Only the expected output of the command.
        """,
    )


class TestCaseList(BaseModel):
    test_case_list: List[TestCase] = Field(
        ...,
        description="A list of test case objects, each with a command and expected output.",
    )


class String(BaseModel):
    """String result of the computation."""

    result: str = Field(
        ...,
        description="The result the computation represented as a string.",
        examples=["42"],
    )
