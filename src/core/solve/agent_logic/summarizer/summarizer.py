from src.utils.state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.solve.agent_logic.sys_prompts import SUMMARIZER_SYSTEM_PROMPT, NEUROSYM_DEFAULT_MODEL
from src.utils.pretty_print import beautify

def get_summary(state: AgentState, token_logger):
    extracted = state["extracted_text"]
    summarizer = ChatOpenAI(temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10, callbacks=[token_logger])

    messages = [
        SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage(content=extracted),
    ]

    response = summarizer.invoke(messages)

    beautify ("SUMMARIZING FINISHED")
    return {**state, "assignment_summary": response.content}