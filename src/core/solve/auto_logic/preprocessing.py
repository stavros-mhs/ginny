import os
import re

from src.utils.state import AgentState
from src.utils.pretty_print import beautify

from src.utils.pdf_to_str import pdftostr
from src.utils.extract_tests import extract_test_cases

def pdftostr_wrapper(state: AgentState):
    extracted = pdftostr(state["messages"][-1].content)

    beautify ("PDF TO STRING CONVERSION FINISHED")
    return {**state, "extracted_text": extracted}


def extract_test_cases_wrapper(state: AgentState):
    test_cases = extract_test_cases(state["extracted_text"])

    beautify ("TEST CASE EXTRACTION FINISHED")
    return {**state, "test_cases": test_cases}

def get_compilation_cmd (state: AgentState):
    print ("enter compiler of choice (for example: gcc, g++, etc.): ")
    compiler_choice = input ("compiler: ")
    print ("enter flags for compiler (-Wall -Wextra -Werror): ")
    flags = input ("flags: ")

    print ("how should the source file be named? (input same name as shown in examples for consistency)")
    source_file_name = input ("source file name: ")

    print ("finally, how should the binary be named? (input same name as shown in test cases for consistency)")
    binary_file_name = input ("binary file name: ")

    return {
		**state,
		"compiler_choice": compiler_choice,
        "flags": flags,
        "source_file_name": source_file_name,
        "binary_file_name": binary_file_name
	}

def prepend_wd (state: AgentState):
    source_file_name = state ["source_file_name"]
    binary_file_name = state ["binary_file_name"]
    test_cases = state ["test_cases"]

    new_source_fn = f"working_dir/{source_file_name}"
    new_binary_fn = f"working_dir/{binary_file_name}"

    bin_pattern = rf"\b{binary_file_name}\b"
    
    new_test_cases = {}
    for cmd, expected_out in test_cases.items ():
        new_cmd = re.sub (bin_pattern, new_binary_fn, cmd)

        new_test_cases [new_cmd] = expected_out

    return {
        **state,
        "test_cases": new_test_cases,
        "source_file_name": new_source_fn,
        "binary_file_name": new_binary_fn
    }

def set_up_wd (state: AgentState):
    os.makedirs ("working_dir", exist_ok=True)