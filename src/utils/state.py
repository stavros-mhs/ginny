from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # chat message history
    
    iter: int # max amount of implementation retries
    current: int # how many tries have been attempted so far

    extracted_text: str # text from pdf given
    test_cases: dict # test cases extracted from pdf in the form of key value pairs <cmd, expected_out>
    assignment_summary: str # assignment synopsis to be passed to implementer agent

    # compilation details
    compiler_choice: str
    flags: str
    source_file_name: str
    binary_file_name: str

    # details about compilation
    compilation_out: str
    exit_code: int

    # we define "test score" as <(passed test cases) / (total number of test cases)>
    accuracy_threshold: float # user's desired test score for an implementation to be accepted
    test_accuracy: float # current iteration's test score. if >= accuracy threshold, implementation is succesful
    
    validation_out: str # detailed analysis of which tests failed and which didn't and why
