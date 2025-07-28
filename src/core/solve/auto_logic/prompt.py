from langchain_core.messages import HumanMessage
from src.utils.state import AgentState
from src.utils.pretty_print import beautify

# CREATE PROMPT FOR IMPLEMENTER
#? MUST BE A CLEANER WAY TO IMPLEMENT THIS
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