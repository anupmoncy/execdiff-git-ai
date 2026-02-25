import argparse
from execdiff_git_ai.agent import run_agent, run_agent_with_ai

def scan():
    """Run the ExecDiff Git AI assessment agent (non-AI mode)."""
    print("🔍 ExecDiff Git AI: Starting impact assessment (non-AI mode)...\n")
    run_agent()

def scan_ai():
    """Run the ExecDiff Git AI assessment agent with AI analysis (Ollama)."""
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
        help="Scan workspace and assess changes (non-AI mode)"
    )
    
    scan_ai_parser = subparsers.add_parser(
        "scan-ai",
        help="Scan workspace with AI-powered analysis (requires Ollama)"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        scan()
    elif args.command == "scan-ai":
        scan_ai()

if __name__ == "__main__":
    main()
