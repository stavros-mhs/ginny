import re


def extract_test_cases(extracted_text: str) -> dict:
    pattern = r"(?m)^\s*\S*\$ (\./[^\n]+)\n\s*([^\n]+)"
    matches = re.findall(pattern, extracted_text)

    return {cmd.strip(): output.strip() for cmd, output in matches}
