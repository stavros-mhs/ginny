from langchain_community.tools import ListDirectoryTool, ReadFileTool, WriteFileTool
from src.core.solve.agent_logic.generics import build_agent
from src.core.solve.agent_logic.sys_prompts import IMPLEMENTER_SYSTEM_PROMPT
from src.utils.state import AgentState


def implementer_wrapper(model, APItimeout):
    implementer = build_agent(model_name=model, APItimeout=APItimeout, temperature=0.8)

    toolbox = [
        ReadFileTool(root_dir="working_dir"),
        WriteFileTool(root_dir="working_dir"),
        ListDirectoryTool(root_dir="working_dir"),
    ]

    implementer = implementer.bind_tools(toolbox)

    return implementer
