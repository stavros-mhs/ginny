import os

from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig
from src.utils.pdf_to_str import pdftostr
from src.utils.extract_tests import extract_test_cases
from src.utils.validate import validate

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_community.tools import ReadFileTool, WriteFileTool

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

IMPLEMENTER_SYSTEM_PROMPT = os.environ.get ("IMPLEMENTER_SYSTEM_PROMPT", """You're a LLM agent node in a workflow meant to implement software for the task provided.
                                _Provide code_. You'll be given tools to write code and read what you wrote to make corrections. 
                                Your code will be given to a validator who will automatically test what you wrote and 
                                if any test case returns an error you'll be required to re-write the implementation.
                                Make sure any inputs expected will be given via argv. _Not_ scanf.
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

    return {
        **state,
        "messages": [response],
        }

def pdftostr_wrapper (state: AgentState):
    extracted = pdftostr (state ["messages"][-1].content)
    return {
        **state,
        "extracted_text": extracted
    }

def extract_test_cases_wrapper (state: AgentState):
    test_cases = extract_test_cases (state ["extracted_text"])
    return {
        **state,
        "test_cases": test_cases
    }

def get_summary (state: AgentState):
    extracted = state["extracted_text"]
    summarizer = ChatOpenAI (temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10)

    messages = [
        SystemMessage (content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage (content=extracted)
    ]

    response = summarizer.invoke (messages)
    
    return {
        **state,
        "assignment_summary": response.content
        }

def create_prompt (state: AgentState):
    assignment_summary = state ["assignment_summary"]
    test_cases = "\n".join (f"{cmd}{exp_out}" for cmd, exp_out in state ["test_cases"].items ())    
    validation_out = state ["validation_out"]

    prompt = assignment_summary + test_cases + validation_out
    
    new_message = state ["messages"] + [HumanMessage (content=prompt)]
    return {
        **state,
        "messages": new_message
        }
    
def validate_wrapper (state: AgentState):
    test_cases = state ["test_cases"]
    validation_out, accuracy = validate (test_cases)

    return {
        **state,
        "validation_out": validation_out,
        "test_accuracy": accuracy
        }

def pass_validation (state: AgentState):
    accuracy = state ["test_accuracy"]
    if accuracy > 0.9:
        return "end"
    else:
        return "try_again"

def iterate ():
    workflow = StateGraph (AgentState, GraphConfig)    

    # defining implementer agent and toolbox
    toolbox = [ReadFileTool (verbose=True), WriteFileTool (verbose=True)]
    implementer = ChatOpenAI (temperature=0.8, model=NEUROSYM_DEFAULT_MODEL)
    implementer = implementer.bind_tools (toolbox)
    impl_toolnode = ToolNode (toolbox)

    # node definitions
    workflow.add_node ("pdf_to_str", pdftostr_wrapper)
    workflow.add_node ("extract_tests", extract_test_cases_wrapper)
    workflow.add_node ("summarizer", get_summary)
    workflow.add_node ("create_prompt", create_prompt)

    workflow.add_node ("implementer", partial (call_model, model=implementer, prompt=IMPLEMENTER_SYSTEM_PROMPT))
    workflow.add_node ("impl_action", impl_toolnode)

    workflow.add_node ("validation", validate_wrapper)

    # set graph's entry point
    workflow.set_entry_point ("pdf_to_str")

    # define graph's edges
    workflow.add_edge ("pdf_to_str", "extract_tests")
    workflow.add_edge ("pdf_to_str", "summarizer")
    workflow.add_edge ("extract_tests", "create_prompt")
    workflow.add_edge ("summarizer", "create_prompt")
    workflow.add_edge ("create_prompt", "implementer")

    workflow.add_conditional_edges ("implementer", should_continue, {"continue": "impl_action", "end": "validation"})
    workflow.add_edge ("impl_action", "implementer")
    
    workflow.add_edge ("implementer", "validation")
    workflow.add_conditional_edges ("validation", pass_validation, {"end": END, "try_again": "create_prompt"})

    # model has memory
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
    initial_state = {
        "messages": [HumanMessage (content=user_in)],
        "extracted_text": "",
        "test_cases": {},
        "implementation": "",
        "validation_out": ""
    }
    final_state = program.invoke (initial_state, config= {"configurable": {"thread_id": 24}, "recursion_limit": 100})
    return final_state ["messages"][-1].content