from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    extracted_text: str
    test_cases: dict
    assignment_summary: str
    compilation_out: str
    exit_code: int
    accuracy_threshold: float
    test_accuracy: float #TODO name this to something better
    validation_out: str
