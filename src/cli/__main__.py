import argparse

from src.cli.summarize import run_goal
from src.cli.implement import run_impl
from src.cli.validate import run_val
from src.cli.solve import run_solve


def main():
    parser = argparse.ArgumentParser(prog="Ginny", description="Ginny's CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # defining spot_goal command
    goal_parser = subparsers.add_parser("summarize", help="sums up pdf given")
    goal_parser.add_argument("pdf_path", help="path to requirments pdf")

    # defining implement command
    impl_parser = subparsers.add_parser(
        "implement", help="implements code for the task given"
    )
    impl_parser.add_argument("goal", help="goal given to Ginny to write code for")

    # defining validate command
    val_parser = subparsers.add_parser(
        "validate", help="confirms given software passes test cases given"
    )
    val_parser.add_argument("pdf_path", help="path to requirments pdf")

    solve_parser = subparsers.add_parser(
        "solve",
        help="attempts to implement a solution according to the requirments given",
    )
    solve_parser.add_argument("pdf_path", help="path to requirments pdf")
    solve_parser.add_argument (
        "--acc",
        type=float,
        default=1.0,
        help="accuracy threshold (float must be between 0.0 and 1.0)"
        )
    solve_parser.add_argument (
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="the model of you choice to implement the software. defaults to gpt-4o-mini."
        )
    solve_parser.add_argument (
        "--iter",
        type=int,
        default=10,
        help="most times the implementation can fail before giving up\ndefault value is 10"
    )
    solve_parser.add_argument (
        "--APItimeout",
        type=int,
        default=500,
        help="time (in seconds) to wait for response from model's API\ndefault value is 500"
    )
    solve_parser.add_argument (
        "--SubprocessTimeout",
        type=int,
        default=30,
        help="""time (in seconds) the LLMs code is allowed to run before stopping\n
                default value is 30
                \n
                \n
                NOTE: depending on the assignment at hand, the code may need to run for more than 30 seconds!
                """
    )

    args = parser.parse_args()

    if args.command == "summarize":
        run_goal(args.pdf_path)
    elif args.command == "implement":
        run_impl(args.goal)
    elif args.command == "validate":
        run_val(args.pdf_path)
    elif args.command == "solve":
        if not 0.0 <= args.acc <= 1.0:
            parser.error ("--acc must be between 0.0 and 1.0")
        if 10 > args.APItimeout:
            parser.error ("--APItimeout must be at least 10")
        if 10 > args.SubprocessTimeout:
            parser.error ("--SubprocessTimeout must be at least 10")
        run_solve(args.pdf_path, args.acc, args.model, args.iter, args.APItimeout, args.SubprocessTimeout)
    else:
        print("unknown command given")


if __name__ == "__main__":
    main()
