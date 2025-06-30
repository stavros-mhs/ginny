from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_community.tools import ReadFileTool, WriteFileTool
from langchain_community.callbacks.openai_info import OpenAICallbackHandler

from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from langchain_core.messages import HumanMessage

from src.core.solve.node_logic import (
    pdftostr_wrapper,
    extract_test_cases_wrapper,
    get_summary,
    create_prompt,
    call_model,
    validate_wrapper,
    should_continue,
    pass_validation,
    compilation_wrapper,
    pass_compilation,
)
from src.core.solve.sys_prompts import IMPLEMENTER_SYSTEM_PROMPT, NEUROSYM_DEFAULT_MODEL

def iterate():
    workflow = StateGraph(AgentState, GraphConfig)

    # defining implementer agent and toolbox
    token_logger = OpenAICallbackHandler() # keep track of token usage
    toolbox = [ReadFileTool(verbose=True), WriteFileTool(verbose=True)]
    implementer = ChatOpenAI(temperature=0.8, model=NEUROSYM_DEFAULT_MODEL, callbacks=[token_logger])
    implementer = implementer.bind_tools(toolbox)
    impl_toolnode = ToolNode(toolbox)

    # node definitions
    workflow.add_node("pdf_to_str", pdftostr_wrapper)
    workflow.add_node("extract_tests", extract_test_cases_wrapper)
    workflow.add_node("summarizer", get_summary)
    workflow.add_node("create_prompt", create_prompt)

    workflow.add_node(
        "implementer",
        partial(call_model, model=implementer, prompt=IMPLEMENTER_SYSTEM_PROMPT, token_logger=token_logger),
    )
    workflow.add_node("impl_action", impl_toolnode)

    workflow.add_node("compilation", compilation_wrapper)
    workflow.add_node("validation", validate_wrapper)

    # set graph's entry point
    workflow.set_entry_point("pdf_to_str")

    # define graph's edges
    workflow.add_edge("pdf_to_str", "extract_tests")
    workflow.add_edge("extract_tests", "summarizer")
    workflow.add_edge("summarizer", "create_prompt")
    workflow.add_edge("create_prompt", "implementer")

    workflow.add_conditional_edges(
        "implementer",
        should_continue,
        {"continue": "impl_action", "end": "compilation"},
    )
    workflow.add_edge("impl_action", "implementer")

    workflow.add_conditional_edges(
        "compilation",
        pass_compilation,
        {"continue": "validation", "retry": "create_prompt"},
    )
    workflow.add_conditional_edges(
        "validation", pass_validation, {"end": END, "try_again": "create_prompt"}
    )

    # model has memory
    checkpointer = MemorySaver()
    # compile graph
    graph = workflow.compile(checkpointer=checkpointer)
    # illustrate graph for debugging
    img = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img)
        # print("Graph written to graph.png")
    return graph


def execute(program, user_in: str, accuracy: float) -> str:
    initial_state = {
        "messages": [HumanMessage(content=user_in)],
        "extracted_text": "",
        "test_cases": {},
        "assignment_summary": "",
        "compilation_out": "",
        "exit_code": -1,
        "test_accuracy": 0.0,
        "accuracy_threshold": accuracy,
        "validation_out": "",
    }
    final_state = program.invoke(
        initial_state,
        config={"configurable": {"thread_id": 24}, "recursion_limit": 100},
    )
    return final_state["messages"][-1].content
