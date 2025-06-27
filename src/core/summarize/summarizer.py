import os

from langchain_openai import ChatOpenAI

from src.utils.state import AgentState
from src.utils.config import GraphConfig

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from langchain_core.messages import HumanMessage, SystemMessage

NEUROSYM_DEFAULT_MODEL = os.environ.get("NEUROSYM_DEFAULT_MODEL", "gpt-4o-mini")


def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    print("==> LLM Response:", last_message.content)
    print("==> Tool Calls:\n", last_message.tool_calls)

    if not last_message.tool_calls:
        print("No tools called.")
        return "end"
    else:
        return "continue"


# this can probs be improved
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    """You're a LLM agent node in a workflow.
                                You'll be given a string containing a coding assignment of undergraduate level difficult from an 'Introduction to Programming' course.
                                The assignment will likely be be in C (but not neccesarilly).
                                What you have to do is summarize the goal of the assignment in a concise way so
                                that whoever's implementing it (another LLM or human) gets the gist of it.
                                Do not mention test cases or details of how to turn in the assignment.
                                Mention _explicitly_ the language in which the assignment must be written in.
                                Maybe choose 1 or 2 examples and add them.
                                In general, keep it _brief_ and _to the point_.

                                You are given the option to iterate before you turn in your summary if you believe you can make it better.
                                """,
)


def call_model(state, config, model, prompt):
    messages = state["messages"]
    messages = [SystemMessage(prompt)] + messages
    response = model.invoke(messages)

    return {"messages": [response]}


def iterate(toolbox):
    workflow = StateGraph(AgentState, GraphConfig)

    # init model, define toolnode and bind tools
    tool_node = ToolNode(toolbox)
    model = ChatOpenAI(temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10)
    model = model.bind_tools(toolbox)

    # node definitions
    workflow.add_node(
        "summarizer", partial(call_model, model=model, prompt=SYSTEM_PROMPT)
    )
    workflow.add_node("action", tool_node)

    # set graph's entry point
    workflow.set_entry_point("summarizer")

    # define graph's edges
    workflow.add_conditional_edges(
        "summarizer",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )
    workflow.add_edge("action", "summarizer")

    # moel has memory
    checkpointer = MemorySaver()
    # compile graph
    graph = workflow.compile(checkpointer=checkpointer)
    # illustrate graph for debugging
    img = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img)
        print("Graph written to graph.png")
        print("Summary written to summary.txt")
    return graph


def execute(program, user_in: str) -> str:
    final_state = program.invoke(
        {"messages": [HumanMessage(content=user_in)]},
        config={"configurable": {"thread_id": 24}, "recursion_limit": 100},
    )
    return final_state["messages"][-1].content
