from src.utils.state import AgentState
from src.utils.pdf_to_str import pdftostr
from src.utils.extract_tests import extract_test_cases
from src.utils.validate import validate
from src.utils.compile import comp
from src.utils.pretty_print import beautify

from langchain_openai import ChatOpenAI
from src.core.solve.sys_prompts import SUMMARIZER_SYSTEM_PROMPT, NEUROSYM_DEFAULT_MODEL

from langchain_core.messages import HumanMessage, SystemMessage


# GENERAL UTILITIES
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    print("==> LLM Response:", last_message.content)
    print("==> Tool Calls:\n", last_message.tool_calls)

    if not last_message.tool_calls:
        print("No tools called.")
        return "end"
    else:
        return "continue"


def call_model(state, config, model, prompt, token_logger):
    messages = state["messages"]
    messages = [SystemMessage(prompt)] + messages
    response = model.invoke(messages)

    beautify ()
    print(f"Tokens Used: {token_logger.total_tokens}\n")
    # print(f"Successful Requests: {token_logger.successful_requests}\n")
    print(f"Total Cost (USD): {token_logger.total_cost:.6f}\n\n")

    return {
        **state,
        "messages": [response],
    }


# NODE SPECIFIC LOGIC
def pdftostr_wrapper(state: AgentState):
    extracted = pdftostr(state["messages"][-1].content)

    beautify ("PDF TO STRING CONVERSION FINISHED")
    return {**state, "extracted_text": extracted}


def extract_test_cases_wrapper(state: AgentState):
    test_cases = extract_test_cases(state["extracted_text"])

    beautify ("TEST CASE EXTRACTION FINISHED")
    return {**state, "test_cases": test_cases}


def get_summary(state: AgentState):
    extracted = state["extracted_text"]
    summarizer = ChatOpenAI(temperature=0.5, model=NEUROSYM_DEFAULT_MODEL, timeout=10)

    messages = [
        SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
        HumanMessage(content=extracted),
    ]

    response = summarizer.invoke(messages)

    beautify ("SUMMARIZING FINISHED")
    return {**state, "assignment_summary": response.content}


# CREATE PROMPT FOR IMPLEMENTER
def create_prompt(state: AgentState):
    assignment_summary = state["assignment_summary"]

    test_cases = "\n".join(
        f"{cmd} w/ expected out {exp_out}"
        for cmd, exp_out in state["test_cases"].items()
    )
    validation_out = state["validation_out"]
    exit_code = state["exit_code"]
    compilation_out = state["compilation_out"]

    # if compiling for the first time
    if exit_code == -1:
        prompt = (
            "Assignment summary is:\n"
            + assignment_summary
            + "\nBelow are the test cases you'll be evaluated on:\n"
            + test_cases
        )
    # else, if compilation failed:
    elif exit_code == 1:
        prompt = (
            "Asignment summary is:\n"
            + assignment_summary
            + "\nBelow are the test cases you'll be evaluated on:\n"
            + test_cases
            + "\n"
            + compilation_out
            + "Did not reach validation step cause compilation failed."
        )
    else:
        prompt = (
            "Assignment summary is:\n"
            + assignment_summary
            + "\n"
            + "Below are the test cases you'll be evaluated on:\n"
            + test_cases
            + "\n"
            + compilation_out
            + "Validation output:"
            + "\n"
            + validation_out
        )

    beautify ("PROMT MADE")
    print (prompt)
    new_message = state["messages"] + [HumanMessage(content=prompt)]
    return {**state, "messages": new_message}


# COMPILATION STEP #! NOT MODULAR -- COMPILES FIXED PATH AND SOURCE CODE!
def compilation_wrapper(state: AgentState):
    exit_code, stderr = comp()
    compilation_out = (
        f"compilation finished with exit code: {exit_code}\nstderr: {stderr}\n"
    )

    return {**state, "exit_code": exit_code, "compilation_out": compilation_out}


def pass_compilation(state: AgentState):
    exit_code = state["exit_code"]
    if not exit_code:
        beautify ("COMPILATION SUCCESSFUL")
        return "continue"
    else:
        beautify ("COMPILATION FAILED")
        return "retry"


# VALIDATION LOGIC
def validate_wrapper(state: AgentState):
    test_cases = state["test_cases"]
    validation_out, accuracy = validate(test_cases)

    return {**state, "validation_out": validation_out, "test_accuracy": accuracy}


def pass_validation(state: AgentState):
    accuracy = state["test_accuracy"]
    accuracy_threshold = state ["accuracy_threshold"]
    if accuracy >= accuracy_threshold:
        beautify ("VALIDATION SUCCESFUL")
        return "end"
    else:
        beautify ("VALIDATION FAILED")
        return "try_again"
