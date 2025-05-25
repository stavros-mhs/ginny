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
from src.core.validation.validation import validate

SG_SYSTEM_PROMPT = os.environ.get ("SYSTEM_PROMPT", """You're a LLM agent node in a workflow.
                                You'll be given a JSON containing a coding assignment of undergraduate level difficult from an 'Introduction to Programming' course.
                                The assignment will likely be be in C (but not neccesarilly).
                                What you have to do is spot the goal of the assignment and summarize it in a concise way so
                                that the person implementing the gets the gist of it.
                                Do not mention test cases or details of how to turn in the assignment.
                                Mention _explicitly_ the language in which the assignment must be written in.
                                Maybe choose 1 or 2 examples and add them.
                                In general, keep it _brief_ and _to the point_.

                                You are given the option to iterate before you turn in your summary if you believe you can make it better.
                                """)

IMPL_SYSTEM_PROMPT = os.environ.get ("SYSTEM_PROMPT", """
                                You're a LLM agent node in a workflow meant to implement software for the task provided. 
                                You'll be given tools to write code and read what you wrote to make corrections. 
                                Your code will be given to a validator who will automatically test what you wrote and 
                                if any test case returns an error you'll be required to re-write the implementation.
                                Make sure any inputs expected will be given via argv. _Not_ scanf.
                                """)

NEUROSYM_DEFAULT_MODEL = os.environ.get ("NEUROSYM_DEFAULT_MODEL", "gpt-4o-mini")

def make_json (state, config):
    pdf_path = state ["messages"][-1].content
    parsed_pdf = pdftojson (pdf_path)
    # print (parsed_pdf)
    return {"parsed_pdf": parsed_pdf}

def get_tests (state, config):
    parsed_pdf = state ["parsed_pdf"]
    test_cases = extract_test_cases (parsed_pdf)
    # print (test_cases)
    return {"test_cases": test_cases}

def call_gs (state, config, model, prompt):
    parsed_pdf = state ["parsed_pdf"]
    
    messages = [{"role": "system", "content": prompt}] + messages + parsed_pdf
    response = model.invoke (messages)

def call_model (state, config, model, prompt):
    messages = state ["messages"]
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user"}
    ]
    response = model.invoke (messages)

def should_continue (state):
    messages = state ["messages"]
    last_message = messages [-1]

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

def solve ():
    workflow = StateGraph (AgentState, GraphConfig)

    workflow.add_node ("make_json", make_json)
    workflow.set_entry_point ("make_json")

    workflow.add_node ("get_tests", get_tests)

    sg_model = ChatOpenAI (temperature=0.8, model=NEUROSYM_DEFAULT_MODEL, timeout=10)
    
    sg_toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    sl_toolnode = ToolNode (sg_toolbox)

    sg_model = sg_model.bind_tools (sg_toolbox)

    workflow.add_node ("spot_goal", partial (call_model, model=sg_model, prompt=SG_SYSTEM_PROMPT))
    #! WORK TO BE DONE HERE

    workflow.add_edge ("make_json", "get_tests")
    workflow.add_edge ("get_tests", END)

    checkpointer = MemorySaver ()
    graph = workflow.compile ()
    return graph

def execute (program, user_in):
    final_state = program.invoke (
        {
            "messages": [HumanMessage (content=user_in)],
            "parsed_pdf": {}
        },
        config = {
            "configurable": {"thread_id": 24},
            "recursion_limit": 100
        }
    )
    return final_state["parsed_pdf"]