def register_subcommand(subparsers):
    parser = subparsers.add_parser("goal-node", help="Run goal node logic")
    # add your own arguments here if needed
    parser.set_defaults(func=run)

def run(args):
    from src.core.validation import main
    main()