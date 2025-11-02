import os
from functools import partial

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from src.utils.config import GraphConfig
from src.utils.state import AgentState

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


SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    """
                                You're a LLM agent node in a workflow meant to implement software for the task provided.
                                _Provide code_. You'll be given tools to write code and read what you wrote to make corrections. 
                                Your code will be given to a validator who will automatically test what you wrote and 
                                if any test case returns an error you'll be required to re-write the implementation.
                                Make sure any inputs expected will be given via argv. _Not_ scanf.
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
    model = ChatOpenAI(temperature=0.5, model=NEUROSYM_DEFAULT_MODEL)
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

    # model has memory
    checkpointer = MemorySaver()
    # compile graph
    graph = workflow.compile(checkpointer=checkpointer)
    # illustrate graph for debugging
    img = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img)
        # TODO inject file name for source code and print it
        print("Graph written to graph.png")
    return graph


def execute(program, user_in: str) -> str:
    final_state = program.invoke(
        {"messages": [HumanMessage(content=user_in)]},
        config={"configurable": {"thread_id": 24}, "recursion_limit": 100},
    )
    return final_state["messages"][-1].content
