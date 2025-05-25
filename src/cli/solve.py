from workflow.graph import solve, execute

def run_solve (pdf_path):
    execute (solve (), pdf_path)