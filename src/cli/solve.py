from src.core.solve.workflow import iterate, execute


def run_solve(pdf_path, accuracy, model, iter):
    program = iterate(model)
    result = execute(program, pdf_path, accuracy, iter)
