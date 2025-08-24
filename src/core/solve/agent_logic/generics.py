from src.core.solve.agent_logic.custom_types.ctypes import String
from src.core.solve.agent_logic.sys_prompts import NEUROSYM_DEFAULT_MODEL, TOKEN_LOGGER

from pydantic import BaseModel
from langchain_core.prompts import (ChatPromptTemplate,
                                    SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate)
from langchain_core.output_parsers import PydanticToolsParser
from langchain_openai import ChatOpenAI

def build_agent(
        temperature: float = 0.0,
        model: str = NEUROSYM_DEFAULT_MODEL,
        token_logger = TOKEN_LOGGER
        ):
    
    """Single function to build agents"""
    agent = ChatOpenAI(
        temperature=temperature, model=model, timeout=10, callbacks=[token_logger]
    )

    return agent

def cast_chain (llm, type: BaseModel = String, token_logger = TOKEN_LOGGER):
    llm = llm
    parser = PydanticToolsParser (tools=[type])

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "You are a tool that converts data to the given type. The type is: {type}"
            ),
            HumanMessagePromptTemplate.from_template(
                "You are given the data: ```{data}```. Convert the data to the given type: {type}."
            ),
        ]
    )

    chain = prompt | llm.bind_tools ([type]) | parser
    return chain