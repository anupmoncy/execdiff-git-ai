import argparse

def main():
    parser = argparse.ArgumentParser(prog="bloksbox", description="Bloksbox CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("trace", help="Trace workspace changes during AI actions")
    subparsers.add_parser("status", help="Show current trace status")

    args = parser.parse_args()

    if args.command == "trace":
        print("Tracing is ON. Use your AI copilot now, hit enter once you are done with the work to see trace")
        input()
        print("Trace complete!")
    
    elif args.command == "status":
        print("Bloksbox v0.0.1 - Ready for testing")
