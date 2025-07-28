from src.utils.state import AgentState
from src.utils.pretty_print import beautify
from src.utils.validate import validate

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