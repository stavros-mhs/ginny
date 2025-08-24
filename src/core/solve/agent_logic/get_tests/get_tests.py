from src.utils.state import AgentState
from src.core.solve.agent_logic.generics import build_agent, cast_chain
from src.core.solve.agent_logic.custom_types.ctypes import TestCaseList
from src.utils.pretty_print import beautify

def get_tests_wrapper (state: AgentState, model, token_logger):
    text = state ["extracted_text"]
    agent = build_agent (model=model, token_logger=token_logger)
    chain = cast_chain (llm=agent, type=TestCaseList)

    chain_out = chain.invoke ({"data": text, "type": TestCaseList})
    #print (f"type of chain: {type(chain_out)}")
    unwrapped_chain = chain_out[0]
    #print (f"type of unwrapped chain: {type (unwrapped_chain)}")

    test_cases_list = unwrapped_chain.test_case_list
    
    print ("\n")
    print (test_cases_list)
    print ("\n")
    
    test_cases_to_dict = [tc.dict () for tc in test_cases_list]

    beautify ("TEST CASES RETRIEVED")
    return {
        **state,
        "test_cases": test_cases_to_dict
    }