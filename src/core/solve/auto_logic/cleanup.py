import os
import shutil

from src.utils.state import AgentState


# save final attempt
def cleanup(state: AgentState):
    src = "working_dir"
    dst = f"snapshots/final"

    # create dir to save in between round progress
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    # cp working dir contents to dst
    shutil.copytree(src, dst, dirs_exist_ok=True)
    shutil.rmtree("working_dir", ignore_errors=True)
