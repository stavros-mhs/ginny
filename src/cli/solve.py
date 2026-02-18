from src.core.solve.workflow import execute, iterate


def run_solve(pdf_path, accuracy, model, iter, APItimeout, SubprocessTimeout):
    program = iterate(model, APItimeout)
    result = execute(program, pdf_path, accuracy, iter, APItimeout, SubprocessTimeout)
