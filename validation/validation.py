import sys
import subprocess
import shlex

from pdf_to_json import pdftojson
from extract_tests import extract_test_cases

def validate (test_cases: dict) -> dict:
    #! BUG WHEN RUNNING SUBPROCESS
    #! CALLS PROGRAM NAME WRAPPED IN SINGLE QUOTES
    testing = dict ()
    for case in test_cases:
        case = case.strip ()
        if (case.startswith("'") and case.endswith("'")) or (case.startswith('"') and case.endswith('"')):
            case = case[1:-1]      

        output = subprocess.run (case, capture_output=True)    
        testing [case] = output.stdout
    
    passed = dict ()
    for out in testing:
        passed [out] = passed [out] != 0

    return passed

if __name__ == "__main__":
    pdf_path = sys.argv [1]
    jsonify_pdf = pdftojson (pdf_path)
    
    test_cases = extract_test_cases (jsonify_pdf)
    
    validation = dict ()
    validate (test_cases)
    