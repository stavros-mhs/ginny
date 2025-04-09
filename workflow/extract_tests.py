import re

def extract_test_cases (json_data: dict) -> dict:
    text = "\n".join (json_data ["pages"])
    pattern = r'(?m)^\s*\S*\$ (\./[^\n]+)\n\s*([^\n]+)'
    matches = re.findall (pattern, text)

    return {cmd.strip (): output.strip () for cmd, output in matches}