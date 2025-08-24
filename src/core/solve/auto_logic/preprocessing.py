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

def set_up_wd (state: AgentState):
    os.makedirs ("working_dir", exist_ok=True)