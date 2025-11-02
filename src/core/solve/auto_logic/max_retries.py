import os
import shutil

from src.utils.state import AgentState


# MAX RETRIES LOGIC
def increment_state(state: AgentState):
    current = state["current"]
    print(f"round: {current + 1}")
    current += 1

    return {**state, "current": current}


def check_limit(state: AgentState):
    current = state["current"]
    max_steps = state["iter"]

    if current >= max_steps:
        return "end"
    else:
        return "continue"


# SAVE IN BETWEEN IMPLEMENTATIONS
def save_in_between(state: AgentState):
    src = "working_dir"

    current = state["current"]
    dst = f"snapshots/round_{current}"

    # create dir to save in between round progress
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    # cp working dir contents to dst
    shutil.copytree(src, dst, dirs_exist_ok=True)
