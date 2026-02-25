import argparse
from execdiff_git_ai.agent import run_agent, run_agent_with_ai

def assess_command():
    """Run the ExecDiff Git AI assessment (non-AI mode)."""
    print("🔍 ExecDiff Git AI: Starting impact assessment (non-AI mode)...\n")
    run_agent()

def ai_assess_command():
    """Run the ExecDiff Git AI assessment with AI analysis."""
    print("🤖 ExecDiff Git AI: Starting AI-powered impact assessment...\n")
    run_agent_with_ai()

def main():
    parser = argparse.ArgumentParser(
        prog="execdiff-git",
        description="ExecDiff Git AI - Analyze AI-driven code changes"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    assess_parser = subparsers.add_parser(
        "assess",
        help="Quick assessment of changes (non-AI mode, no setup required)"
    )
    
    ai_assess_parser = subparsers.add_parser(
        "ai-assess",
        help="AI-powered assessment with business-facing analysis (requires Ollama)"
    )
    
    args = parser.parse_args()
    
    if args.command == "assess":
        assess_command()
    elif args.command == "ai-assess":
        ai_assess_command()

if __name__ == "__main__":
    main()
