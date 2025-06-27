import shlex
import subprocess
import io


def validate(test_cases: dict) -> str:
    passed = 0
    log_stream = io.StringIO()

    for command, expected_out in test_cases.items():
        cmd = shlex.split(command)

        log_stream.write(f"testing: <{command}> -- ")
        log_stream.write(f"expecting: <{expected_out}> -- ")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            log_stream.write(f"stdout: <{stdout}>\n")

            if stdout == expected_out:
                passed += 1
                log_stream.write(f"[PASS]: {command}\n")
            else:
                # print(
                #    f"FAILED IN COMMAND: {command}. Expected {expected_out} and got {stdout}"
                # )
                log_stream.write(f"[FAIL]: {command}\n")
                if stderr:
                    log_stream.write(f"stderr: {stderr}\n")

        except subprocess.TimeoutExpired:
            # print(
            #    f"FAILED IN COMMAND: {command}. Expected {expected_out} and got subprocess.TimeoutExpired"
            # )
            log_stream.write(f"\n[FAIL]: {command} -- ")
            log_stream.write(
                "<subprocess.TimeoutExpired> - test case runs for 10 seconds and time limit got exceeded\n"
            )

    result = log_stream.getvalue()
    log_stream.close()
    accuracy = passed / len(test_cases)

    return result, accuracy
