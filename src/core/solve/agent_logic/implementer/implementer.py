from src.utils.state import AgentState
from src.core.solve.agent_logic.sys_prompts import IMPLEMENTER_SYSTEM_PROMPT
from src.core.solve.agent_logic.generics import build_agent

from langchain_community.tools import ReadFileTool, WriteFileTool, ListDirectoryTool

def implementer_wrapper (model, token_logger, APItimeout):
    implementer = build_agent (
        APItimeout=APItimeout,
        temperature=0.8,
        model=model,
        token_logger=token_logger
    )
    
    toolbox = [
        ReadFileTool(root_dir="working_dir"),
        WriteFileTool(root_dir="working_dir"),
        ListDirectoryTool (root_dir="working_dir")
    ]

    implementer = implementer.bind_tools (toolbox)

    return implementer