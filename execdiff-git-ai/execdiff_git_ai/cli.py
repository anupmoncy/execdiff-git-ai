import argparse
import subprocess
import sys
from execdiff_git_ai.agent import run_agent, run_agent_with_ai

def check_ollama_installed():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def prompt_install_ollama():
    """Ask user for permission to install Ollama."""
    print("\n" + "="*80)
    print("🤖 Ollama Not Found")
    print("="*80)
    print("\nAI mode requires Ollama (free, open-source local LLM).")
    print("Would you like to install it now?")
    print("\nInstallation will:")
    print("  • Download Ollama (100-200MB)")
    print("  • Install to your system")
    print("  • Allow you to use AI-powered code analysis")
    print("\nYou can skip this and use non-AI mode instead.")
    
    while True:
        response = input("\nInstall Ollama? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("Please enter 'yes' or 'no'")

def install_ollama():
    """Install Ollama based on the operating system."""
    import platform
    system = platform.system()
    
    print("\n📥 Installing Ollama...")
    print("This may take a few minutes...\n")
    
    try:
        if system == "Darwin":  # macOS
            print("Installing for macOS using Homebrew...")
            subprocess.run(["brew", "install", "ollama"], check=True)
        elif system == "Linux":
            print("Installing for Linux...")
            subprocess.run(
                ["curl", "-fsSL", "https://ollama.ai/install.sh"],
                stdout=subprocess.PIPE,
                check=True
            )
            subprocess.run(["sh"], input="curl -fsSL https://ollama.ai/install.sh | sh", check=True)
        elif system == "Windows":
            print("Please download Ollama from https://ollama.ai/")
            print("Windows installation requires manual download.")
            return False
        else:
            print(f"Unsupported system: {system}")
            return False
        
        print("\n✅ Ollama installed successfully!")
        print("\nTo start using AI mode:")
        print("  1. Start Ollama server: ollama serve")
        print("  2. In another terminal: execdiff-git scan-ai")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error during installation: {e}")
        return False

def scan_command():
    """Run the ExecDiff Git AI assessment (non-AI mode)."""
    print("🔍 ExecDiff Git AI: Starting impact assessment (non-AI mode)...\n")
    run_agent()

def scan_ai_command():
    """Run the ExecDiff Git AI assessment with AI analysis."""
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\n⚠️  Ollama is not installed.")
        if prompt_install_ollama():
            if not install_ollama():
                print("\nFalling back to non-AI mode...")
                scan_command()
                return
        else:
            print("\nFalling back to non-AI mode...")
            print("(Install Ollama later to enable AI analysis)")
            scan_command()
            return
    
    # Check if Ollama server is running
    if not check_ollama_running():
        print("\n⚠️  Ollama server is not running.")
        print("\nTo use AI mode, start Ollama in another terminal:")
        print("  ollama serve")
        print("\nThen try again: execdiff-git scan-ai")
        print("\nFalling back to non-AI mode for now...\n")
        scan_command()
        return
    
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
        help="Scan workspace with AI-powered analysis (optional, requires Ollama)"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        scan_command()
    elif args.command == "scan-ai":
        scan_ai_command()

if __name__ == "__main__":
    main()
