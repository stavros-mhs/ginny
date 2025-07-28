import sys
import shlex
import subprocess

#from src.utils.pdf_to_json import pdftojson
#from src.utils.extract_tests import extract_test_cases


def validate(test_cases: dict):
    passed = 0
    logs = open("logs.txt", "w")

    for command, expected_out in test_cases.items():
        cmd = shlex.split(command)

        logs.write(f"testing: <{command}> ")
        logs.write(f"expected: <{expected_out}>\n")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=11)
            logs.write(f"stdout: <{result.stdout.strip ()}>\n")
            if result.stdout.strip() == expected_out:
                print(f"[PASS]: {command}")
                passed += 1
            else:
                print(f"[FAIL]: {command}")
                logs.write(f"stderr: <{result.stderr.strip ()}\n")
        except subprocess.TimeoutExpired as e:
            print(f"[FAIL]: {command}")
            logs.write("<subprocess timeout>\n")

    logs.close()
    return passed / len(test_cases)


#if __name__ == "__main__":
#    pdf_path = sys.argv[1]
#    jsonify_pdf = pdftojson(pdf_path)
#    test_cases = extract_test_cases(jsonify_pdf)
#
#    validate(test_cases)
