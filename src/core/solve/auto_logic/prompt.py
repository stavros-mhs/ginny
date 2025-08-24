from langchain_core.messages import HumanMessage
from src.utils.state import AgentState
from src.utils.pretty_print import beautify

def printable_test_cases (test_cases):
    """get test cases list from state and make them human readable"""

    lines = []
    # test_cases is a list of dicts
    for case in test_cases:
        cmd = ' '.join (case ["command"])
        exp_out = case ["expected_out"]
        line = f"Command: {cmd} w/ expected out: {exp_out}"
        lines.append (line)

    return '\n'.join (line for line in lines)

# CREATE PROMPT FOR IMPLEMENTER
def create_prompt(state: AgentState):
    assignment_summary = state["assignment_summary"]
    test_cases_list_printable = printable_test_cases (state ["test_cases"])

    validation_out = state["validation_out"]
    exit_code = state["exit_code"]
    compilation_out = state["compilation_out"]

    # if compiling for the first time
    if exit_code == -1:
        prompt = (
            "Assignment summary is:\n"
            + assignment_summary
            + "\nBelow are the test cases you'll be evaluated on:\n"
            + test_cases_list_printable
        )
    # else, if compilation failed:
    elif exit_code == 1:
        prompt = (
            "Asignment summary is:\n"
            + assignment_summary
            + "\nBelow are the test cases you'll be evaluated on:\n"
            + test_cases_list_printable
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
            + test_cases_list_printable
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