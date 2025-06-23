import os

from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig
from src.utils.pdf_to_str import pdftostr
from src.utils.extract_tests import extract_test_cases

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from langchain_core.messages import HumanMessage, SystemMessage

NEUROSYM_DEFAULT_MODEL = os.environ.get ("NEUROSYM_DEFAULT_MODEL", "gpt-4o-mini")

# this can probs be improved
SUMMARIZER_SYSTEM_PROMPT = os.environ.get ("SUMMARIZER_SYSTEM_PROMPT", """You're a LLM agent node in a workflow.
                                You'll be given a string containing a coding assignment of undergraduate level difficult from an 'Introduction to Programming' course.
                                The assignment will likely be be in C (but not neccesarilly).
                                What you have to do is summarize the goal of the assignment in a concise way so
                                that whoever's implementing it (another LLM or human) gets the gist of it.
                                Do not mention test cases or details of how to turn in the assignment.
                                Mention _explicitly_ the language in which the assignment must be written in.
                                Maybe choose 1 or 2 examples and add them.
                                In general, keep it _brief_ and _to the point_.

                                You are given the option to iterate before you turn in your summary if you believe you can make it better.
                                """)

def should_continue (state):
    messages = state ["messages"]
    last_message = messages [-1]
    print("==> LLM Response:", last_message.content)
    print("==> Tool Calls:\n", last_message.tool_calls)

    if not last_message.tool_calls:
        print ("No tools called.")
        return "end"
    else:
        return "continue"

def call_model (state, config, model, prompt):
    messages = state ["messages"]
    messages = [SystemMessage (prompt)] + messages
    response = model.invoke (messages)

    return {"messages": [response]}

def pdftostr_wrapper (state: AgentState):
    extracted = pdftostr (state ["messages"][-1].content)
    return {
        "extracted_text": extracted
    }

def extract_test_cases_wrapper (state: AgentState):
    test_cases = extract_test_cases (state ["extracted_text"])
    return {
        "test_cases": test_cases
    }

def get_sumamry (state: AgentState):
    extracted = state["extracted_text"]
    summarizer = ChatOpenAI (temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10)

    messages = [
        SystemMessage (content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage (content=extracted)
    ]

    response = summarizer.invoke (messages)
    return {"assignment_summary": response.content}

def show_res (state: AgentState):
    print (">> EXTRACTED TEXT:\n")
    print (state ["extracted_text"])
    print ("\n")
    print (">> EXTRACTED TEST CASES\n")
    for test_case in state["test_cases"]:
        print (test_case)
    print (">> SUMMARY MADE:\n")
    print (state ["assignment_summary"])
    print ("\n")
    return {"messages": "done"}

def iterate ():
    workflow = StateGraph (AgentState, GraphConfig)    

    # node definitions
    workflow.add_node ("pdf_to_str", pdftostr_wrapper)
    workflow.add_node ("extract_tests", extract_test_cases_wrapper)
    workflow.add_node ("summarizer", get_sumamry)
    workflow.add_node ("show_res", show_res)

    # set graph's entry point
    workflow.set_entry_point ("pdf_to_str")

    # define graph's edges
    workflow.add_edge ("pdf_to_str", "extract_tests")
    workflow.add_edge ("pdf_to_str", "summarizer")
    workflow.add_edge ("extract_tests", "show_res")
    workflow.add_edge ("summarizer", "show_res")

    # moel has memory
    checkpointer = MemorySaver ()
    # compile graph
    graph = workflow.compile (checkpointer=checkpointer)
    # illustrate graph for debugging
    img = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img)
        print("Graph written to graph.png")
    return graph

def execute (program, user_in:str) -> str:
    final_state = program.invoke ({"messages": [HumanMessage (content=user_in)]}, config= {"configurable": {"thread_id": 24}, "recursion_limit": 100})
    return final_state ["messages"][-1].content