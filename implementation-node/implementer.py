import os

from langchain_openai import ChatOpenAI

from utils.state import AgentState
from utils.config import GraphConfig

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from langchain_core.messages import HumanMessage

NEUROSYM_DEFAULT_MODEL = os.environ.get ("NEUROSYM_DEFAULT_MODEL", "gpt-4o-mini")

def should_continue (state):
    messages = state ["messages"]
    last_message = messages [-1]

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# this can def be improved
SYSTEM_PROMPT = os.environ.get ("SYSTEM_PROMPT", """
                                You're a LLM agent node in a workflow meant to implement software for the task provided. 
                                You'll be given tools to write code and read what you wrote to make corrections. 
                                Your code will be given to a validator who will automatically test what you wrote and 
                                if any test case returns an error you'll be required to re-write the implementation.
                                Make sure any inputs expected will be given via argv. _Not_ scanf

                                
                                """)

def call_model (state, config, model):
    messages = state ["messages"]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = model.invoke (messages)

    return {"messages": [response]}

def iterate (toolbox):
    workflow = StateGraph (AgentState, GraphConfig)
    tool_node = ToolNode (toolbox)

    model = ChatOpenAI (temperature=0.5, model=NEUROSYM_DEFAULT_MODEL)
    model = model.bind_tools (toolbox)

    workflow.add_node ("implementer", partial (call_model, model=model))
    workflow.set_entry_point ("implementer")

    workflow.add_node ("action", tool_node)
    workflow.add_conditional_edges ("implementer", should_continue, {"continue": "action", "end": END,},)

    checkpointer = MemorySaver ()
    graph = workflow.compile (checkpointer=checkpointer)
    return graph

# got no clue what some of these mean in a deep sense
def execute (program, user_in:str) -> str:
    final_state = program.invoke ({"messages": [HumanMessage (content=user_in)]}, config= {"configurable": {"thread_id": 24}, "recursion_limit": 100})
    return final_state ["messages"][-1].content