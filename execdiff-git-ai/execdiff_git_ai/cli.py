import argparse
from execdiff_git_ai.agent import run_agent, run_agent_with_ai

def scan_command():
    """Run the ExecDiff Git AI assessment (non-AI mode)."""
    print("🔍 ExecDiff Git AI: Starting impact assessment (non-AI mode)...\n")
    run_agent()

def scan_ai_command():
    """Run the ExecDiff Git AI assessment with AI analysis."""
    print("🤖 ExecDiff Git AI: Starting AI-powered impact assessment...\n")
    run_agent_with_ai()

def main():
    parser = argparse.ArgumentParser(
        prog="execdiff-git",
        description="ExecDiff Git AI - Analyze AI-driven code changes"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan workspace and assess changes (non-AI mode, always available)"
    )
    
    scan_ai_parser = subparsers.add_parser(
        "scan-ai",
        help="Scan workspace with AI-powered analysis (automatically manages Ollama)"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        scan_command()
    elif args.command == "scan-ai":
        scan_ai_command()

if __name__ == "__main__":
    main()
