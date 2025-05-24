import os

from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig

from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from langgraph.graph import StateGraph, END

from langgraph.prebuilt import ToolNode
from langchain_community.tools import ReadFileTool, WriteFileTool

from src.utils.pdf_to_json import pdftojson
from workflow.extract_tests import extract_test_cases
from src.core.validation.validation import validate

GS_SYSTEM_PROMPT = os.environ.get ("SYSTEM_PROMPT", """You're a LLM agent node in a workflow.
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

def make_json (state, config, pdf_path):
    make_json = pdftojson (pdf_path)
    return {"parsed_pdf": make_json}

def get_tests (state, config):
    tests = extract_test_cases (state ["parsed_pdf"])
    return {"test_cases": tests}

def call_model (state, config, model, prompt):
    messages = state ["messages"]
    messages = [{"role": "system", "content": prompt}] + messages
    response = model.invoke (messages)

def should_continue (state):
    messages = state ["messages"]
    last_message = messages [-1]

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

def valid_tests (state, config):
    if validate (state ["test_cases"]):
        pass
    else:
        pass

def solve (pdf_path):
    workflow = StateGraph (AgentState, GraphConfig) # define graph

    workflow.add_node ("make_json", )