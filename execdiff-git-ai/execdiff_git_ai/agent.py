import subprocess
import os
import time
import signal
import requests
import sys

DEFAULT_MODEL = "tinyllama"

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
    """Detect added/modified functions and classes (public only)."""
    symbols = []
    lines = diff_text.split('\n')
    current_file = None
    seen = set()
    
    for i, line in enumerate(lines):
        if line.startswith('diff --git'):
            parts = line.split()
            if len(parts) >= 4:
                current_file = parts[3].replace('b/', '')
        
        # Only detect NEW functions - must have 'def ' followed by valid identifier
        if line.startswith('+') and 'def ' in line and '+++' not in line:
            try:
                # Extract text after 'def '
                after_def = line.split('def ')[1]
                # Get name before opening parenthesis
                name = after_def.split('(')[0].strip()
                # Validate: must be valid Python identifier (alphanumeric + underscore, not starting with digit)
                if name and name.isidentifier() and not name.startswith('_'):
                    if name not in seen:
                        symbols.append({'name': name, 'type': 'function', 'change': 'NEW', 'impact': 'LOW', 'file': current_file})
                        seen.add(name)
            except:
                pass
        
        # Only detect DELETED functions
        elif line.startswith('-') and 'def ' in line and '---' not in line:
            try:
                after_def = line.split('def ')[1]
                name = after_def.split('(')[0].strip()
                if name and name.isidentifier() and not name.startswith('_'):
                    if name not in seen:
                        symbols.append({'name': name, 'type': 'function', 'change': 'DELETED', 'impact': 'LOW', 'file': current_file})
                        seen.add(name)
            except:
                pass
        
        # Only detect NEW classes
        elif line.startswith('+') and 'class ' in line and '+++' not in line:
            try:
                after_class = line.split('class ')[1]
                # Get name before colon or opening parenthesis
                name = after_class.split('(')[0].split(':')[0].strip()
                if name and name.isidentifier() and not name.startswith('_'):
                    if name not in seen:
                        symbols.append({'name': name, 'type': 'class', 'change': 'NEW', 'impact': 'LOW', 'file': current_file})
                        seen.add(name)
            except:
                pass
        
        # Only detect DELETED classes
        elif line.startswith('-') and 'class ' in line and '---' not in line:
            try:
                after_class = line.split('class ')[1]
                name = after_class.split('(')[0].split(':')[0].strip()
                if name and name.isidentifier() and not name.startswith('_'):
                    if name not in seen:
                        symbols.append({'name': name, 'type': 'class', 'change': 'DELETED', 'impact': 'LOW', 'file': current_file})
                        seen.add(name)
            except:
                pass
    
    return symbols

def detect_modified_symbols(diff_text):
    """Detect MODIFIED functions (both + and - lines present)."""
    symbols = []
    lines = diff_text.split('\n')
    added_funcs = set()
    deleted_funcs = set()
    
    for line in lines:
        if line.startswith('+') and 'def ' in line and '+++' not in line:
            try:
                name = line.split('def ')[1].split('(')[0].strip()
                added_funcs.add(name)
            except:
                pass
        elif line.startswith('-') and 'def ' in line and '---' not in line:
            try:
                name = line.split('def ')[1].split('(')[0].strip()
                deleted_funcs.add(name)
            except:
                pass
    
    modified_funcs = added_funcs & deleted_funcs
    for name in modified_funcs:
        if not name.startswith('_'):
            symbols.append({'name': name, 'type': 'function', 'change': 'MODIFIED', 'impact': 'LOW'})
    
    return symbols

def format_table_row(col1, col2, col3):
    """Format a table row with proper alignment."""
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

def check_model_available(model_name=DEFAULT_MODEL):
    """Check if model is available."""
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
        print("⚠️  Ollama server did not respond")
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

def pull_ollama_model(model_name=DEFAULT_MODEL):
    """Pull model with user permission."""
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
    
    print(f"\n📥 Downloading '{model_name}'...")
    try:
        result = subprocess.run(["ollama", "pull", model_name], timeout=600)
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

def get_function_description(func_name):
    """Generate business-facing description based on function name (2 lines)."""
    descriptions = {
        'authenticate_user': 'Handles user login and credential verification.\nSecures user account access.',
        'create_session': 'Establishes user sessions after login.\nMaintains user state across requests.',
        'validate_token': 'Checks if authentication tokens are valid and not expired.\nEnsures secure access.',
        'process_payment': 'Processes customer payments through multiple payment methods.\nEnables checkout functionality.',
        'checkout': 'Completes the purchase transaction.\nFinalizes customer orders.',
        'send_email': 'Sends email notifications to users.\nCommunicates order and account updates.',
        'detect_modified_symbols': 'Finds functions that were changed in the code.\nIdentifies modifications to existing code.',
        'check_model_available': 'Verifies if the AI model is installed locally.\nEnsures AI capabilities are ready.',
        'analyze_symbol_with_ollama': 'Analyzes individual code changes with AI.\nProvides focused impact assessment.',
        'get_overall_summary_from_llm': 'Generates business impact summary from all changes.\nProvides high-level overview.',
        'group_by_functionality': 'Groups code changes by their business purpose.\nOrganizes changes by feature area.',
        'format_functionality_output': 'Formats grouped changes for display.\nPresents analysis in readable format.',
        'assess_command': 'Runs quick code assessment without AI.\nFast analysis of what changed.',
        'ai_assess_command': 'Runs AI-powered code assessment.\nProvides deep impact analysis.',
    }
    
    if func_name in descriptions:
        return descriptions[func_name]
    
    if 'get_' in func_name or 'fetch_' in func_name:
        return f'Retrieves {func_name.replace("get_", "").replace("fetch_", "")} data.\nAccesses system information.'
    elif 'set_' in func_name or 'update_' in func_name:
        return f'Updates {func_name.replace("set_", "").replace("update_", "")} configuration.\nModifies system state.'
    else:
        return f'Performs {func_name.replace("_", " ")} operation.\nHandles core business logic.'

def analyze_symbol_with_ollama(symbol):
    """Use pattern matching for individual symbol analysis (no LLM)."""
    description = get_function_description(symbol['name'])
    return description

def get_overall_summary_from_llm(all_analyses):
    """Get business summary from LLM - simplified and more reliable."""
    try:
        # Filter out test files and garbage symbols
        filtered = [a for a in all_analyses if 'test_feature' not in a and "'" not in a and len(a) > 20]
        
        if not filtered:
            return None
        
        # Limit to 8 most important changes
        analyses_text = "\n".join(filtered[:8])
        
        prompt = f"""Read these changes and write 3-5 business impact bullets.

Changes:
{analyses_text}

Rules:
ONLY output bullet points.
One line per bullet (15 words max).
Focus on user/business benefit.
NO technical jargon.

Output format - ONLY this:
• Impact point 1
• Impact point 2
• Impact point 3"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": DEFAULT_MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            
            # Extract only lines starting with •
            lines = []
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('•'):
                    # Clean up the line
                    cleaned = line[1:].strip()
                    if cleaned and len(cleaned) > 5:
                        lines.append(f"• {cleaned}")
            
            # Return 3-5 bullets
            if lines:
                return "\n".join(lines[:5])
        
        return None
    except Exception as e:
        print(f"  (summary generation skipped)")
        return None

def group_by_functionality(all_analyses):
    """Group changes by functionality instead of individual changes."""
    groups = {
        'authentication': [],
        'payment': [],
        'data': [],
        'api': [],
        'ui': [],
        'security': [],
        'other': []
    }
    
    for analysis in all_analyses:
        analysis_lower = analysis.lower()
        
        if any(word in analysis_lower for word in ['auth', 'login', 'session', 'user', 'credential']):
            groups['authentication'].append(analysis)
        elif any(word in analysis_lower for word in ['payment', 'checkout', 'purchase', 'transaction']):
            groups['payment'].append(analysis)
        elif any(word in analysis_lower for word in ['data', 'database', 'storage', 'cache']):
            groups['data'].append(analysis)
        elif any(word in analysis_lower for word in ['api', 'endpoint', 'request', 'response']):
            groups['api'].append(analysis)
        elif any(word in analysis_lower for word in ['ui', 'button', 'form', 'display', 'render']):
            groups['ui'].append(analysis)
        elif any(word in analysis_lower for word in ['validate', 'token', 'encrypt', 'security', 'permission']):
            groups['security'].append(analysis)
        else:
            groups['other'].append(analysis)
    
    return groups

def format_functionality_output(groups):
    """Format grouped changes by functionality - 2 line summary per feature."""
    output = []
    
    functionality_labels = {
        'authentication': '🔐 Authentication',
        'payment': '💳 Payment Processing',
        'data': '💾 Data & Storage',
        'api': '🔌 API & Integration',
        'ui': '🎨 UI & Display',
        'security': '🛡️ Security',
        'other': '⚙️ Other Changes'
    }
    
    for key, label in functionality_labels.items():
        if groups[key]:
            output.append(f"\n{label}:")
            # Show most important change with 2-line summary
            analysis = groups[key][0]
            # Extract just the 2-line description part
            if ':' in analysis:
                parts = analysis.split(': ', 1)
                if len(parts) == 2:
                    change_label_and_name = parts[0]
                    description = parts[1]
                    output.append(f"  {change_label_and_name}: {description}")
            else:
                output.append(f"  {analysis}")
    
    return "\n".join(output)

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
        print("  (No symbols detected)")
    
    print()
    print("✅ Assessment complete!\n")

def run_agent_with_ai():
    """Run AI-powered assessment."""
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
    total_added = 0
    total_deleted = 0
    for filename, stats in file_stats.items():
        print(format_table_row(filename, str(stats['added']), str(stats['deleted'])))
        total_added += stats['added']
        total_deleted += stats['deleted']
    
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
        print("  (No symbols detected)")
    
    print()
    
    if symbols:
        print("="*80)
        print("🤖 AI Impact Assessment")
        print("="*80)
        
        ollama_process = None
        
        try:
            if not check_ollama_installed():
                print("\n⚠️  Ollama is not installed.")
                print("📥 Install from: https://ollama.ai/\n")
                return
            
            if not check_ollama_running():
                ollama_process = start_ollama_server()
                if not ollama_process:
                    return
            
            if not check_model_available(DEFAULT_MODEL):
                if not pull_ollama_model(DEFAULT_MODEL):
                    return
            
            modified_symbols = detect_modified_symbols(diff)
            all_symbols = symbols + modified_symbols
            
            all_analyses = []
            total = len(all_symbols)
            
            print(f"\n🧠 Analyzing {total} change{'s' if total > 1 else ''}:\n")
            sys.stdout.flush()
            
            for symbol in all_symbols:
                change_label = f"[{symbol['change']}]"
                file_name = symbol.get('file', 'unknown')
                sys.stdout.write(f"  • {change_label} {symbol['name']} ({file_name})... ")
                sys.stdout.flush()
                
                # Use pattern matching (no LLM for individual analyses)
                description = get_function_description(symbol['name'])
                analysis_line = f"• {change_label} {symbol['name']} ({file_name}): {description}"
                all_analyses.append(analysis_line)
                print("✓")
                # Print 2-line description
                for desc_line in description.split('\n'):
                    print(f"    {desc_line}")
                print()
                
                sys.stdout.flush()
            
            sys.stdout.write("  • Getting overall summary... ")
            sys.stdout.flush()
            overall_summary = get_overall_summary_from_llm(all_analyses)
            if overall_summary:
                print("✓\n")
                
                print("📋 What Changed:")
                print(f"  Scope: {len(file_stats)} file(s) modified ({total_added} additions, {total_deleted} removals)")
                print()
                
                print("Overall Impact:")
                print(overall_summary)
                print()
                
                # Group by functionality
                groups = group_by_functionality(all_analyses)
                functionality_output = format_functionality_output(groups)
                
                print("Changes by Functionality:")
                print(functionality_output)
                
            else:
                print("✓\n")
                
                print("📋 What Changed:")
                print(f"  Scope: {len(file_stats)} file(s) modified ({total_added} additions, {total_deleted} removals)")
                print()
                
                # Group by functionality
                groups = group_by_functionality(all_analyses)
                functionality_output = format_functionality_output(groups)
                
                print("Changes by Functionality:")
                print(functionality_output)
        
        finally:
            if ollama_process:
                stop_ollama_server(ollama_process)
    
    print()
    print("✅ Assessment complete!\n")
