import sys
import shlex
import subprocess

from utils.pdf_to_json import pdftojson
from workflow.extract_tests import extract_test_cases

def validate (test_cases: dict):
    passed = 0

    for command, expected_out in test_cases.items ():
        cmd = shlex.split (command)

        result = subprocess.run (cmd, capture_output=True, text=True, timeout=11)
        result_out = result.stdout.strip ()
        # error_out = result.stderr.strip ()

        if result_out == expected_out:
            print (f'[PASS]: {command}')
            passed += 1
        else:
            print (f'[FAIL]: {command}')
            print (f'EXPECTED: {expected_out!r}')
            # print (f'GOT     : {result_out!r}')

            # if error_out:
            #     print (f'STDERR: {error_out!r}')
    print (f'CASES PASSED: {passed}')


if __name__ == "__main__":
    pdf_path = sys.argv [1]
    jsonify_pdf = pdftojson (pdf_path)
    test_cases = extract_test_cases (jsonify_pdf)
    
    validate (test_cases)
    