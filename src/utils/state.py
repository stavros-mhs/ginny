from src.core.solve.agent_logic.custom_types.ctypes import CompilationCMD, TestCaseList
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # chat message history
    
    APItimeout: int # time (in seconds) to wait for LLM response
    SubprocessTimeout: int # time (in seconds) to run LLM's code

    iter: int # max amount of implementation retries
    current: int # how many tries have been attempted so far

    extracted_text: str # text from pdf given
    assignment_summary: str # assignment synopsis to be passed to implementer agent
    comp_cmd: CompilationCMD # comp_cmd is of Type List [str]
    test_cases: TestCaseList # test_cases_list is of Type List[TestCase]

    # details about compilation
    compilation_out: str
    exit_code: int

    # we define "test score" as <(passed test cases) / (total number of test cases)>
    accuracy_threshold: float # user's desired test score for an implementation to be accepted
    test_accuracy: float # current iteration's test score. if >= accuracy threshold, implementation is succesful
    
    validation_out: str # detailed analysis of which tests failed and which didn't and why
