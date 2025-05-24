from src.utils.pdf_to_json import pdftojson
from workflow.extract_tests import extract_test_cases
from src.core.validation.validation import validate

def run_val (pdf_path):
    make_to_json = pdftojson (pdf_path)
    test_cases = extract_test_cases (make_to_json)
    validate (test_cases)