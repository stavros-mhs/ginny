from src.core.solve.agent_logic.custom_types.ctypes import String
from src.core.solve.agent_logic.sys_prompts import NEUROSYM_DEFAULT_MODEL

from pydantic import BaseModel
from langchain_core.prompts import (ChatPromptTemplate,
                                    SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate)
from langchain_core.output_parsers import PydanticToolsParser

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI


#def build_agent(
#        APItimeout: int,
#        temperature: float = 0.0,
#        model: str = NEUROSYM_DEFAULT_MODEL,
#        token_logger = TOKEN_LOGGER
#        ):
#    
#    """Single function to build agents"""
#    agent = ChatOpenAI(
#        temperature=temperature, model=model, timeout=APItimeout, callbacks=[token_logger]
#    )
#
#    return agent


def build_agent (
    model_name: str,
    APItimeout: int,
    temperature: float = 0.0,
    ):

    """
    infers the model's provider from model_name
    builds the appropriate chat model
    """

    if model_name.startswith ("gpt-") or "gpt" in model_name.lower ():
        return ChatOpenAI (
            model=model_name,
            temperature=temperature,
            timeout=APItimeout
        )
    
    elif model_name.startswith ("claude-") or "claude" in model_name.lower ():
        return ChatAnthropic (
            model=model_name,
            temperature=temperature,
            timeout=APItimeout
        )

    elif model_name.startswith ("gemini-") or "gemini" in model_name.lower ():
        return ChatGoogleGenerativeAI (
            model=model_name,
            temperature=temperature,
            timeout=APItimeout
            )
    else:
        raise ValueError (
            f"Cannot determine provider for for model: {model_name}.\n"
            f"Supported models must start with 'gpt', 'claude' or 'gemini'."
            )

def cast_chain (llm, type: BaseModel = String):
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