import os

from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig

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

# this can probs be improved
SYSTEM_PROMPT = os.environ.get ("SYSTEM_PROMPT", """You're a LLM agent node in a workflow.
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
#? Would writing the output and providing it with read access yield better results?
#TODO can also test one shot w/o iteration capabilities 

def call_model (state, config, model, prompt):
    messages = state ["messages"]
    messages = [{"role": "system", "content": prompt}] + messages
    response = model.invoke (messages)

    return {"messages": [response]}

def iterate (toolbox):
    workflow = StateGraph (AgentState, GraphConfig)
    tool_node = ToolNode (toolbox)

    model = ChatOpenAI (temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10)
    model = model.bind_tools (toolbox)

    workflow.add_node ("spot_goal", partial (call_model, model=model, prompt=SYSTEM_PROMPT))
    workflow.set_entry_point ("spot_goal")

    workflow.add_node ("action", tool_node)
    workflow.add_conditional_edges ("spot_goal", should_continue, {"continue": "action", "end": END,},)

    checkpointer = MemorySaver ()
    graph = workflow.compile (checkpointer=checkpointer)
    return graph

# got no clue what some of these mean in a deep sense
def execute (program, user_in:str) -> str:
    final_state = program.invoke ({"messages": [HumanMessage (content=user_in)]}, config= {"configurable": {"thread_id": 24}, "recursion_limit": 100})
    return final_state ["messages"][-1].content