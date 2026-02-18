import io
import os
import subprocess

from src.utils.pretty_print import beautify
from src.utils.state import AgentState
from src.utils.validate import validate

# VALIDATION LOGIC
# def validate_wrapper(state: AgentState):
#    test_cases = state["test_cases"]
#    validation_out, accuracy = validate(test_cases)
#
#    return {**state, "validation_out": validation_out, "test_accuracy": accuracy}


def validate(state: AgentState):
    cwd = os.getcwd()
    os.chdir("working_dir")

    test_cases = state["test_cases"]
    SubprocessTimeout = state["SubprocessTimeout"]

    passed = 0
    log_stream = io.StringIO()

    for case in test_cases:
        cmd = case["command"]
        exp_out = case["expected_out"]

        log_stream.write(f"testing: <{cmd}> -- ")
        log_stream.write(f"expecting: <{exp_out}> -- ")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=SubprocessTimeout
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            log_stream.write(f"stdout: <{stdout}>\n")

            if stdout == exp_out:
                passed += 1
                log_stream.write(f"[PASS]: {cmd}\n")
            else:
                log_stream.write(f"[FAIL]: {cmd}\n")
                if stderr:
                    log_stream.write(f"stderr: {stderr}\n")
        except subprocess.TimeoutExpired:
            log_stream.write(f"\n[FAIL]: {cmd} -- ")
            log_stream.write(
                f"<subprocess.TimeoutExpired> - test case runs for {SubprocessTimeout} seconds and time limit got exceeded\n"
            )

    validation_out = log_stream.getvalue()
    log_stream.close()
    accuracy = passed / len(test_cases)

    os.chdir(cwd)
    return {**state, "validation_out": validation_out, "test_accuracy": accuracy}


def pass_validation(state: AgentState):
    accuracy = state["test_accuracy"]
    accuracy_threshold = state["accuracy_threshold"]
    if accuracy >= accuracy_threshold:
        beautify("VALIDATION SUCCESFUL")
        return "end"
    else:
        beautify("VALIDATION FAILED")
        return "try_again"
