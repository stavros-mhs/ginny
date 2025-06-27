import subprocess

def comp ():
    compiler = "gcc"
    flags = ["-O0", "-m32", "-Wall", "-Wextra", "-Werror", "-pedantic", "-o"]
    target = "collatz"
    source_file = "collatz.c"

    result = subprocess.run (
        [compiler, *flags, target, source_file],
        capture_output=True,
        text=True
    )

    exit_code = result.returncode
    stderr = result.stderr.strip ()

    return exit_code, stderr