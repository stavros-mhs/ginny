from src.core.solve.workflow import iterate, execute


def run_solve(pdf_path, accuracy):
    program = iterate()
    result = execute(program, pdf_path, accuracy)
