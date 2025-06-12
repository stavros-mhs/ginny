import os

from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig

from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from langgraph.graph import StateGraph, END

from langgraph.prebuilt import ToolNode
from langchain_community.tools import ReadFileTool, WriteFileTool
from langchain_core.messages import HumanMessage

from src.utils.pdf_to_json import pdftojson
from workflow.extract_tests import extract_test_cases
from workflow.read_json import ReadParsedPDF
from src.core.validation.validation import validate

SG_SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    """You're a LLM agent node in a workflow. You will be given a prompt that contains the goal of a coding assignment.
                                   It contains a coding assignment of undergraduate level difficult from an 'Introduction to Programming' course.
                                   The assignment will likely be be in C (but not neccesarilly).
                                   What you have to do is spot the goal of the assignment and summarize it in a concise way so
                                   that the person implementing the gets the gist of it.
                                   Do _not_ mention test cases or details of how to turn in the assignment.
                                   Mention _explicitly_ the language in which the assignment must be written in.
                                   Maybe choose 1 or 2 examples and add them. In general, keep it _brief_ and _to the point_.
                                   You are given the option to iterate before you turn in your summary if you believe you can make it better.
                                """,
)

IMPL_SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    """
                                You're a LLM agent node in a workflow meant to implement software for the task provided.
                                You'll be given tools to write code and read what you wrote to make corrections.
                                Your code will be given to a validator who will automatically test what you wrote and
                                if any test case returns an error you'll be required to re-write the implementation.
                                Make sure any inputs expected will be given via argv. _Not_ scanf.
                                """,
)

NEUROSYM_DEFAULT_MODEL = os.environ.get("NEUROSYM_DEFAULT_MODEL", "gpt-4o-mini")


def extract_text(state, config):
    pdf_path = state["messages"][-1].content
    extracted_text = "\n\n".join(pdftojson(pdf_path)["pages"])
    print("extract_text", extracted_text)
    return {"extracted_text": extracted_text}


def get_tests(state, config):
    extracted_text = state["extracted_text"]
    test_cases = extract_test_cases(extracted_text)
    print("get_tests", test_cases)
    return {"test_cases": test_cases}


def call_model(state, config, model, prompt):
    messages = state["messages"]
    messages = [{"role": "system", "content": prompt}] + messages
    response = model.invoke(messages)
    print("Model response: ", response, "to the prompt: ", prompt)
    return {"messages": [response]}


def summarize(state, config, model, prompt):
    summary_text = state["extracted_text"]
    # initialize messages as human message with the summary text
    messages = [HumanMessage(content=summary_text)]
    messages = [{"role": "system", "content": prompt}] + messages
    response = model.invoke(messages)
    summary = response.content
    print("Model response: ", response, "to the prompt: ", prompt)
    return {"messages": [response], "assignment_summary": summary}


def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]

    print("should_continue?", last_message.tool_calls, messages[-1])
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


def solve():
    workflow = StateGraph(AgentState, GraphConfig)

    # =======NODE DEFINITIONS=======#
    workflow.add_node("extract_text", extract_text)
    workflow.set_entry_point("extract_text")  #! entry point

    workflow.add_node("get_tests", get_tests)

    # =======SPOT GOAL + SG TOOLS=======#
    summarizer_model = ChatOpenAI(
        temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10
    )

    # sg_toolbox = [WriteFileTool(verbose=True), ReadParsedPDF]
    # sg_toolnode = ToolNode(sg_toolbox)

    # summarizer_model = summarizer_model.bind_tools(sg_toolbox)

    workflow.add_node(
        "summarizer",
        partial(summarize, model=summarizer_model, prompt=SG_SYSTEM_PROMPT),
    )
    # workflow.add_node("sg_action", sg_toolnode)

    # =======EDGE DEFINITIONS=======#
    workflow.add_edge("extract_text", "get_tests")
    workflow.add_edge("get_tests", "summarizer")

    # workflow.add_conditional_edges(
    #     "summarizer", should_continue, {"continue": "sg_action", "end": END}
    # )
    # workflow.add_edge("sg_action", "summarizer")

    workflow.add_edge("summarizer", END)

    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    return graph


def execute(program, user_in):
    final_state = program.invoke(
        {
            "messages": [HumanMessage(content=user_in)],
            "extracted_text": "",
            "assignment_summary": "",
            "implementation": "",
            "test_cases": {},
        },
        config={"configurable": {"thread_id": 24}, "recursion_limit": 100},
    )
    print("I just computed the final state, here are the contents")
    print("extracted_text", final_state["extracted_text"])
    print("assignment_summary", final_state["assignment_summary"])
    print("implementation", final_state["implementation"])
    print("test_cases", final_state["test_cases"])
