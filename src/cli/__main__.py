import argparse

from src.cli.spot_goal import run_goal
from src.cli.implement import run_impl
from src.cli.validate import run_val
from src.cli.solve import run_solve

def main ():
    parser = argparse.ArgumentParser (prog="ginny", description="Ginny\'s CLI")
    subparsers = parser.add_subparsers (dest="command", required=True)

    # defining spot_goal command
    goal_parser = subparsers.add_parser ("spot_goal", help="spots the goal on the pdf given")
    goal_parser.add_argument ("pdf_path", help="path to requirments pdf")

    # defining implement command
    impl_parser = subparsers.add_parser ("implement", help="implements code for the task given")
    impl_parser.add_argument ("goal", help="goal given to Ginny to write code for")

    # defining validate command
    val_parser = subparsers.add_parser ("validate", help="confirms given software passes test cases given")
    val_parser.add_argument ("pdf_path", help="path to requirments pdf")

    solve_parser = subparsers.add_parser ("solve", help="attempts to implement a solution according to the requirments given")
    solve_parser.add_argument ("pdf_path", help="path to requirments pdf")

    args = parser.parse_args ()

    if args.command == "spot_goal":
        run_goal (args.pdf_path)
    elif args.command == "implement":
        run_impl (args.goal)
    elif args.command == "validate":
        run_val (args.pdf_path)
    elif args.command == "solve":
        run_solve (args.pdf_path)
    else:
        print ("unknown command given")

if __name__ == "__main__":
    main ()