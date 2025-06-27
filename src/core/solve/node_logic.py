from src.utils.state import AgentState
from src.utils.pdf_to_str import pdftostr
from src.utils.extract_tests import extract_test_cases
from src.utils.validate import validate
from src.utils.compile import comp

from langchain_openai import ChatOpenAI
from src.core.solve.sys_prompts import SUMMARIZER_SYSTEM_PROMPT, NEUROSYM_DEFAULT_MODEL

from langchain_core.messages import HumanMessage, SystemMessage

# GENERAL UTILITIES
def should_continue (state):
    messages = state ["messages"]
    last_message = messages [-1]
    print("==> LLM Response:", last_message.content)
    # print("==> Tool Calls:\n", last_message.tool_calls)

    if not last_message.tool_calls:
        print ("No tools called.")
        return "end"
    else:
        return "continue"

def call_model (state, config, model, prompt):
    messages = state ["messages"]
    messages = [SystemMessage (prompt)] + messages
    response = model.invoke (messages)

    return {
        **state,
        "messages": [response],
        }

# NODE SPECIFIC LOGIC
def pdftostr_wrapper (state: AgentState):
    extracted = pdftostr (state ["messages"][-1].content)
    return {
        **state,
        "extracted_text": extracted
    }

def extract_test_cases_wrapper (state: AgentState):
    test_cases = extract_test_cases (state ["extracted_text"])
    return {
        **state,
        "test_cases": test_cases
    }

def get_summary (state: AgentState):
    extracted = state["extracted_text"]
    summarizer = ChatOpenAI (temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10)

    messages = [
        SystemMessage (content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage (content=extracted)
    ]

    response = summarizer.invoke (messages)
    
    return {
        **state,
        "assignment_summary": response.content
        }

# CREATE PROMPT FOR IMPLEMENTER
def create_prompt (state: AgentState):
    assignment_summary = state ["assignment_summary"]
    test_cases = "\n".join (f"{cmd}{exp_out}" for cmd, exp_out in state ["test_cases"].items ())    
    validation_out = state ["validation_out"]
    exit_code = state ["exit_code"]
    compilation_out = state ["compilation_out"]

    # if compiling for the first time
    if exit_code == -1:
        prompt = assignment_summary + test_cases + validation_out    
    else:
        prompt = assignment_summary + test_cases + str (exit_code) + compilation_out + validation_out
    
    new_message = state ["messages"] + [HumanMessage (content=prompt)]
    return {
        **state,
        "messages": new_message
        }

# COMPILATION STEP #! NOT MODULAR -- COMPILES FIXED PATH AND SOURCE CODE!
def compilation_wrapper (state: AgentState):
    exit_code, stderr = comp ()
    compilation_out = f"compilation finished with exit code: {exit_code}\nstderr {stderr}:"

    return {
        **state,
        "exit_code": exit_code,
        "compilation_out": compilation_out
    }

def pass_compilation (state: AgentState):
    exit_code = state ["exit_code"]
    if not exit_code:
        return "continue"
    else:
        return "retry"

# VALIDATION LOGIC
def validate_wrapper (state: AgentState):
    test_cases = state ["test_cases"]
    validation_out, accuracy = validate (test_cases)

    return {
        **state,
        "validation_out": validation_out,
        "test_accuracy": accuracy
        }

def pass_validation (state: AgentState):
    accuracy = state ["test_accuracy"]
    if accuracy > 0.9:
        return "end"
    else:
        return "try_again"