import sys

from pdf_to_json import pdftojson
from extract_tests import extract_test_cases

if __name__ == "__main__":
    pdf_path = sys.argv [1]

    json_from_pdf = pdftojson (pdf_path)
    test_cases = extract_test_cases (json_from_pdf)

    for case in test_cases:
        print (case, test_cases [case])