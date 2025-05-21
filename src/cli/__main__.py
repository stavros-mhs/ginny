import argparse

from src.cli.spot_goal import run_goal
from src.cli.implement import run_impl

def main ():
    parser = argparse.ArgumentParser (prog="Ginny", description="Ginny\'s CLI")
    subparsers = parser.add_subparsers (dest="command", required=True)

    # defining spot_goal command
    goal_parser = subparsers.add_parser ("spot_goal", help="spots the goal on the pdf given")
    goal_parser.add_argument ("pdf_path", help="path to pdf for analysis")

    # defining implement command
    impl_parser = subparsers.add_parser ("implement", help="implements code for the task given")
    impl_parser.add_argument ("goal", help="goal given to Ginny to write code for")

    args = parser.parse_args ()

    if args.command == "spot_goal":
        run_goal (args.pdf_path)
    elif args.command == "implement":
        run_impl (args.goal)


if __name__ == "__main__":
    main ()