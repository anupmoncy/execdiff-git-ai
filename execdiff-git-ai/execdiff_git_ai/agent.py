import subprocess
import os
import time
import signal
import requests

def get_git_diff():
    """Get the git diff for staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""

def parse_diff_stats(diff_text):
    """Parse diff to get file-level statistics."""
    files = {}
    current_file = None
    for line in diff_text.split('\n'):
        if line.startswith('diff --git'):
            parts = line.split()
            if len(parts) >= 4:
                current_file = parts[3].replace('b/', '')
                files[current_file] = {'added': 0, 'deleted': 0}
        elif current_file and line.startswith('+') and not line.startswith('+++'):
            files[current_file]['added'] += 1
        elif current_file and line.startswith('-') and not line.startswith('---'):
            files[current_file]['deleted'] += 1
    return files

def detect_changed_symbols(diff_text):
    """Detect added/modified functions, classes, and variables."""
    symbols = []
    lines = diff_text.split('\n')
    current_file = None
    
    for i, line in enumerate(lines):
        if line.startswith('diff --git'):
            parts = line.split()
            if len(parts) >= 4:
                current_file = parts[3].replace('b/', '')
        
        if line.startswith('+') and 'def ' in line:
            try:
                name = line.split('def ')[1].split('(')[0].strip()
                symbols.append({'name': name, 'type': 'function', 'change': 'added', 'impact': 'LOW', 'file': current_file})
            except:
                pass
        elif line.startswith('+') and 'class ' in line:
            try:
                name = line.split('class ')[1].split(':')[0].split('(')[0].strip()
                symbols.append({'name': name, 'type': 'class', 'change': 'added', 'impact': 'LOW', 'file': current_file})
            except:
                pass
        elif line.startswith('+') and '=' in line and 'def ' not in line and 'class ' not in line:
            try:
                var_name = line.split('=')[0].strip().replace('+', '').strip()
                if var_name and not var_name.startswith('#') and var_name.isidentifier():
                    symbols.append({'name': var_name, 'type': 'variable', 'change': 'added', 'impact': 'LOW', 'file': current_file})
            except:
                pass
    return symbols

def format_table_row(col1, col2, col3):
    return f"{col1:<32} {col2:<20} {col3:>8}"

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama_server():
    """Start Ollama server in background."""
    try:
        print("🚀 Starting Ollama server...")
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp if os.name != 'nt' else None
        )
        print("⏳ Waiting for Ollama server to start...")
        for i in range(15):
            time.sleep(1)
            if check_ollama_running():
                print("✅ Ollama server is ready!")
                return process
        print("⚠️  Ollama server did not respond in time")
        process.terminate()
        return None
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return None

def stop_ollama_server(process):
    """Stop Ollama server."""
    if process:
        try:
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            print("🛑 Ollama server stopped")
        except:
            pass

DEFAULT_MODEL = "tinyllama"  # Smallest Ollama model ~637MB

def pull_ollama_model(model_name=DEFAULT_MODEL):
    """Pull an Ollama model with user permission."""
    print(f"\n⚠️  Model '{model_name}' (~637MB) is not installed locally.")
    print(f"✅ Everything stays local - no data is sent to the cloud.\n")
    
    while True:
        response = input(f"Download '{model_name}' now? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            break
        elif response in ["no", "n"]:
            print("⏩ Skipping AI analysis.")
            return False
        else:
            print("Please enter 'yes' or 'no'")
    
    print(f"\n📥 Downloading '{model_name}'... (this may take a minute)")
    try:
        result = subprocess.run(["ollama", "pull", model_name], timeout=300)
        if result.returncode == 0:
            print(f"✅ Model '{model_name}' is ready!")
            return True
        else:
            print(f"❌ Failed to pull model")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Download timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_model_available(model_name=DEFAULT_MODEL):
    """Check if a specific Ollama model is available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            for m in models:
                if model_name in m.get("name", ""):
                    return True
        return False
    except:
        return False

def analyze_with_ollama(diff_text, symbols):
    """Use Ollama API to analyze git diff. Uses tinyllama model by default."""
    ollama_process = None
    model_name = DEFAULT_MODEL
    
    try:
        if not check_ollama_installed():
            print("\n⚠️  Ollama is not installed.")
            print("Ollama is a free, open-source local AI runtime (~50MB).")
            print("✅ Everything stays local - no data is sent to the cloud.")
            print("\n📥 Install from: https://ollama.ai/\n")
            return "⏩ Ollama required. Install and try again."
        
        if not check_ollama_running():
            ollama_process = start_ollama_server()
            if not ollama_process:
                return "❌ Could not start Ollama server."
        
        # Check if model is available, if not ask to pull
        if not check_model_available(model_name):
            if not pull_ollama_model(model_name):
                return "⏩ AI analysis skipped."
        
        # Build prompt
        symbol_list = ", ".join([s['name'] for s in symbols])
        prompt = f"""Analyze these code changes. For each symbol, provide:
- Symbol name
- Impact: LOW/MEDIUM/HIGH  
- Summary: what changed and business impact

Symbols: {symbol_list}

Diff:
{diff_text[:2000]}"""

        print(f"🧠 Analyzing with AI ({model_name}, 100% local)...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            return f"❌ API error: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return "❌ AI analysis timed out."
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        if ollama_process:
            stop_ollama_server(ollama_process)

def run_agent():
    """Run the ExecDiff Git AI assessment (non-AI mode)."""
    print("\n" + "="*30)
    print("📊 File Change Assessment")
    print("="*30)
    
    diff = get_git_diff()
    
    if not diff.strip():
        print("(No staged changes detected)")
        print("\n✅ Assessment complete!\n")
        return
    
    file_stats = parse_diff_stats(diff)
    
    print(format_table_row("File", "+Lines", "-Lines"))
    print("-" * 48)
    for filename, stats in file_stats.items():
        print(format_table_row(filename, str(stats['added']), str(stats['deleted'])))
    
    print("\n" + "-" * 32)
    print()
    
    symbols = detect_changed_symbols(diff)
    
    print("="*80)
    print("📋 Impact Summary")
    print("="*80)
    print(format_table_row("Symbol", "Change Type", "Impact"))
    print("-" * 56)
    
    if symbols:
        for symbol in symbols:
            change_desc = f"{symbol['type']} {symbol['change']}"
            print(format_table_row(symbol['name'], change_desc, symbol['impact']))
    else:
        print("  (No symbols detected in this diff)")
    
    print()
    print("✅ Assessment complete!\n")

def run_agent_with_ai():
    """Run the ExecDiff Git AI assessment with AI-powered analysis."""
    print("\n" + "="*30)
    print("📊 File Change Assessment")
    print("="*30)
    
    diff = get_git_diff()
    
    if not diff.strip():
        print("(No staged changes detected)")
        print("\n✅ Assessment complete!\n")
        return
    
    file_stats = parse_diff_stats(diff)
    
    print(format_table_row("File", "+Lines", "-Lines"))
    print("-" * 48)
    for filename, stats in file_stats.items():
        print(format_table_row(filename, str(stats['added']), str(stats['deleted'])))
    
    print("\n" + "-" * 32)
    print()
    
    symbols = detect_changed_symbols(diff)
    
    print("="*80)
    print("📋 Impact Summary")
    print("="*80)
    print(format_table_row("Symbol", "Change Type", "Impact"))
    print("-" * 56)
    
    if symbols:
        for symbol in symbols:
            change_desc = f"{symbol['type']} {symbol['change']}"
            print(format_table_row(symbol['name'], change_desc, symbol['impact']))
    else:
        print("  (No symbols detected in this diff)")
    
    print()
    
    # AI Analysis
    print("="*80)
    print("🤖 AI Impact Assessment")
    print("="*80)
    print()
    
    ai_analysis = analyze_with_ollama(diff, symbols)
    print(ai_analysis)
    
    print()
    print("✅ Assessment complete!\n")
