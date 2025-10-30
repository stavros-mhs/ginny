from src.utils.state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.solve.agent_logic.sys_prompts import SUMMARIZER_SYSTEM_PROMPT
from src.utils.pretty_print import beautify
from src.core.solve.agent_logic.generics import build_agent

def get_summary(state: AgentState, model):
    extracted = state["extracted_text"]
    APItimeout = state ["APItimeout"]

    summarizer = build_agent (model_name=model, APItimeout=APItimeout, temperature=0.5)

    messages = [
        SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage(content=extracted),
    ]

    response = summarizer.invoke(messages)

    beautify ("SUMMARIZING FINISHED")
    return {**state, "assignment_summary": response.content}