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
from src.core.solve.agent_logic.sys_prompts import IMPLEMENTER_SYSTEM_PROMPT

from src.core.solve.auto_logic.generics import (
    call_model,
    should_continue
)

from src.core.solve.auto_logic.preprocessing import (
    pdftostr_wrapper,
    set_up_wd
)

from src.core.solve.auto_logic.max_retries import (
    increment_state,
    check_limit,
    save_in_between
)

from src.core.solve.auto_logic.compilation import (
    compilation_wrapper,
    pass_compilation
)

from src.core.solve.auto_logic.validation import (
    validate,
    pass_validation
)

from src.core.solve.auto_logic.cleanup import cleanup

from src.core.solve.auto_logic.prompt import create_prompt

from src.core.solve.agent_logic.summarizer.summarizer import get_summary
from src.core.solve.agent_logic.get_comp.get_comp import get_comp_cmd_wrapper
from src.core.solve.agent_logic.get_tests.get_tests import get_tests_wrapper
from src.core.solve.agent_logic.implementer.implementer import implementer_wrapper

def iterate(model):
    workflow = StateGraph(AgentState, GraphConfig)

    # defining implementer agent and toolbox
    token_logger = OpenAICallbackHandler() # init token logger to keep track of token usage
    
    toolbox = [
        ReadFileTool(root_dir="working_dir", verbose=True),
        WriteFileTool(root_dir="working_dir", verbose=True)
    ]
    implementer = implementer_wrapper (model=model, token_logger=token_logger)
    impl_toolnode = ToolNode(toolbox)

    # node definitions
    workflow.add_node("pdf_to_str", pdftostr_wrapper)

    workflow.add_node(
        "extract_tests",
        partial (get_tests_wrapper, model=model, token_logger=token_logger)
        )
    
    workflow.add_node (
        "get_compilation_cmd",
        partial (get_comp_cmd_wrapper, model=model, token_logger=token_logger)
        )
    
    workflow.add_node ("set_up_wd", set_up_wd)
    workflow.add_node ("save_in_between", save_in_between)
    workflow.add_node ("increment_state", increment_state)

    workflow.add_node(
        "summarizer",
        partial (get_summary, model=model, token_logger=token_logger)
        )
    
    workflow.add_node("create_prompt", create_prompt)
    #? redundant token logger usage?
    workflow.add_node(
        "implementer",
        partial(call_model, model=implementer, prompt=IMPLEMENTER_SYSTEM_PROMPT, token_logger=token_logger),
    )
    workflow.add_node("impl_action", impl_toolnode)

    workflow.add_node ("compilation", compilation_wrapper)
    workflow.add_node("validation", validate)
    workflow.add_node ("cleanup", cleanup)

    # set graph's entry point
    workflow.set_entry_point("pdf_to_str")

    # define graph's edges
    workflow.add_edge("pdf_to_str", "summarizer") # user_in.pdf --> summarizes user_in.pdf to a string
    workflow.add_edge ("summarizer", "get_compilation_cmd") # retrieve from summary the  how the source file should be compiled
    workflow.add_edge ("get_compilation_cmd", "extract_tests") # retrieve from the summary the test cases
    workflow.add_edge ("extract_tests", "set_up_wd") # create working_dir
    workflow.add_edge ("set_up_wd", "increment_state") # start tracking attempts
    workflow.add_edge ("save_in_between", "increment_state")

    # if attempt limit reached, end
    workflow.add_conditional_edges (
        "increment_state",
        check_limit,
        {"end": "cleanup", "continue": "create_prompt"}
    )

    workflow.add_edge ("create_prompt", "implementer")

    workflow.add_conditional_edges(
        "implementer",
        should_continue,
        {"continue": "impl_action", "end": "compilation"}, # if no tool was used, proceed to compilation
    )
    workflow.add_edge("impl_action", "implementer") # if some tool was used, go to agent

    workflow.add_conditional_edges(
        "compilation",
        pass_compilation,
        {"continue": "validation", "retry": "save_in_between"}, # if compilation was succefull, go to validation, else retry
    )
    workflow.add_conditional_edges(
        "validation", pass_validation, {"end": "cleanup", "try_again": "save_in_between"}
    )

    workflow.add_edge ("cleanup", END)

    # model has memory
    checkpointer = MemorySaver()
    # compile graph
    graph = workflow.compile(checkpointer=checkpointer)
    
    # illustrate graph for debugging
    img = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img)
        print("Graph written to graph.png")
    return graph


def execute(program, user_in: str, accuracy: float, iter: int) -> str:
    initial_state = {
        "messages": [HumanMessage(content=user_in)],
        "iter": iter,
        "current": 0,
        "extracted_text": "",
        "assignment_summary": "",
        "comp_cmd": "",
        "test_cases": [],
        "compilation_out": [],
        "exit_code": -1,
        "accuracy_threshold": accuracy,
        "test_accuracy": 0.0,
        "validation_out": "",
    }

    final_state = program.invoke(
        initial_state,
        config={"configurable": {"thread_id": 24}, "recursion_limit": 100},
    )
    return final_state["messages"][-1].content
