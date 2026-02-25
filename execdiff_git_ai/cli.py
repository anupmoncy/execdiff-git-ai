import argparse

def scan():
    print("execdiff-git-ai: Scanning workspace for AI-driven code changes...")

def main():
    parser = argparse.ArgumentParser(prog="execdiff", description="ExecDiff Git AI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan_parser = subparsers.add_parser("scan", help="Scan workspace for changes")
    args = parser.parse_args()
    if args.command == "scan":
        scan()
