from src.utils.state import AgentState
from src.core.solve.agent_logic.generics import build_agent, cast_chain
from src.core.solve.agent_logic.custom_types.ctypes import CompilationCMD
from src.utils.pretty_print import beautify

def get_comp_cmd_wrapper (state: AgentState, model):
    
    text = state ["extracted_text"]
    APItimeout = state ["APItimeout"]

    agent = build_agent (model_name=model, APItimeout=APItimeout)
    chain = cast_chain (llm=agent, type=CompilationCMD)

    chain_out = chain.invoke ({"data": text, "type": CompilationCMD})
    comp_cmd = chain_out[0].compilation_cmd # unwrap

    beautify ("COMPILATION COMMAND RETRIEVED")

    print ("\n")
    print (comp_cmd)
    print ("\n")

    return {
        **state,
        "comp_cmd": comp_cmd
    }