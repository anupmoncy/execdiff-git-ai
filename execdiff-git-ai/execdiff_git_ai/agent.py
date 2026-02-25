import subprocess
import os
import re

def get_git_diff():
    """Get the current git diff for unstaged changes."""
    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return "No git repository found or no changes detected."

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
    """
    Parse the diff and extract changed symbols (functions, classes, methods).
    Returns a list of dictionaries with symbol info.
    """
    symbols = []
    lines = diff_text.split('\n')
    modified_functions = set()
    
    for i, line in enumerate(lines):
        # Detect added/modified functions
        if line.startswith('+') and ('def ' in line or 'class ' in line):
            if 'def ' in line:
                try:
                    name = line.split('def ')[1].split('(')[0].strip()
                    symbols.append({
                        'name': name,
                        'type': 'function',
                        'change': 'added',
                        'risk': 'LOW'
                    })
                except:
                    pass
            elif 'class ' in line:
                try:
                    name = line.split('class ')[1].split(':')[0].split('(')[0].strip()
                    symbols.append({
                        'name': name,
                        'type': 'class',
                        'change': 'added',
                        'risk': 'LOW'
                    })
                except:
                    pass
        # Detect modified functions (lines that have @@ context)
        elif line.startswith('@@'):
            for j in range(i+1, min(i+15, len(lines))):
                if lines[j].startswith('-') and 'def ' in lines[j]:
                    try:
                        name = lines[j].split('def ')[1].split('(')[0].strip()
                        if name not in [s['name'] for s in symbols]:
                            modified_functions.add(name)
                    except:
                        pass
        # Detect variables
        elif line.startswith('+') and '=' in line and 'def ' not in line and 'class ' not in line:
            try:
                var_name = line.split('=')[0].strip().replace('+', '').strip()
                if var_name and not var_name.startswith('#') and var_name.isidentifier():
                    symbols.append({
                        'name': var_name,
                        'type': 'variable',
                        'change': 'added',
                        'risk': 'LOW'
                    })
            except:
                pass
    
    # Add modified functions to symbols
    for func in modified_functions:
        symbols.append({
            'name': func,
            'type': 'function',
            'change': 'modified',
            'risk': 'LOW'
        })
    
    return symbols

def format_table_row(col1, col2, col3):
    """Format a table row with proper alignment."""
    return f"{col1:<32} {col2:<20} {col3:>8}"

def run_agent():
    """Run the ExecDiff Git AI assessment (non-AI mode)."""
    print("\n" + "="*30)
    print("📊 File Change Assessment")
    print("="*30)
    
    diff = get_git_diff()
    
    if not diff or diff == "No git repository found or no changes detected.":
        print("(No changes detected)")
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
    print(format_table_row("Symbol", "Change Type", "Risk"))
    print("-" * 56)
    
    if symbols:
        for symbol in symbols:
            change_desc = f"{symbol['type']} {symbol['change']}"
            print(format_table_row(symbol['name'], change_desc, symbol['risk']))
    
    print()
    print("✅ Assessment complete!\n")

def analyze_with_ollama(diff_text, symbols):
    """
    Use Ollama to analyze the git diff and provide AI-powered impact assessment.
    """
    try:
        prompt = f"""Analyze these code changes and provide an impact assessment for each modified symbol.

For each symbol, provide:
- File: <filename>
- Symbol: <name>
- Impact: <LOW/MEDIUM/HIGH>
- Summary: <one-line explanation of the change and its impact>

Changed symbols to analyze: {', '.join([s['name'] for s in symbols])}

Git Diff (first 2000 chars):
{diff_text[:2000]}

Format your response as:
File: <filename> - Symbol: <name>
Impact: <LOW/MEDIUM/HIGH>
Summary: <explanation>
"""
        
        result = subprocess.run(
            ["ollama", "run", "llama2", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return "AI analysis failed. Make sure Ollama is installed and running."
    except FileNotFoundError:
        return "Ollama not found. Install from https://ollama.ai/"
    except subprocess.TimeoutExpired:
        return "AI analysis timed out."
    except Exception as e:
        return f"AI analysis error: {str(e)}"

def extract_impact_summary(ai_analysis):
    """Extract a summary of changes from AI analysis."""
    summary_lines = []
    
    # Count impacts
    high_count = ai_analysis.count("Impact: HIGH")
    medium_count = ai_analysis.count("Impact: MEDIUM")
    low_count = ai_analysis.count("Impact: LOW")
    
    if high_count > 0:
        summary_lines.append(f"🔴 {high_count} HIGH impact change(s)")
    if medium_count > 0:
        summary_lines.append(f"🟡 {medium_count} MEDIUM impact change(s)")
    if low_count > 0:
        summary_lines.append(f"🟢 {low_count} LOW impact change(s)")
    
    return summary_lines

def extract_change_summary(ai_analysis, file_stats, symbols):
    """Extract a user-facing summary by translating technical changes into business requirements."""
    summary_lines = []
    
    # Parse AI analysis to extract business-level impacts
    lines = ai_analysis.split('\n')
    business_needs = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if "Impact: HIGH" in line:
            # Extract the summary for this HIGH impact change
            for j in range(i, min(i+10, len(lines))):
                if "Summary:" in lines[j]:
                    summary_text = lines[j].replace("Summary:", "").strip()
                    # Combine with next lines if they're part of the summary
                    k = j + 1
                    while k < len(lines) and lines[k].strip() and not "Impact:" in lines[k] and not "File:" in lines[k]:
                        summary_text += " " + lines[k].strip()
                        k += 1
                    if summary_text:
                        business_needs.append(("critical", summary_text[:120]))
                    break
        i += 1
    
    # Count impact levels
    high_count = ai_analysis.count("Impact: HIGH")
    medium_count = ai_analysis.count("Impact: MEDIUM")
    low_count = ai_analysis.count("Impact: LOW")
    
    # Extract file changes
    total_files = len(file_stats)
    total_added = sum(stats['added'] for stats in file_stats.values())
    total_deleted = sum(stats['deleted'] for stats in file_stats.values())
    
    # Generate business/user-facing summary
    if high_count > 0:
        if business_needs:
            requirement = business_needs[0][1]
            summary_lines.append(f"🔴 Critical: {requirement}")
        else:
            summary_lines.append(f"🔴 Critical: {high_count} {'change' if high_count == 1 else 'changes'} requiring careful validation")
    
    if medium_count > 0:
        summary_lines.append(f"🟡 Important: {medium_count} {'change' if medium_count == 1 else 'changes'} needing thorough testing and QA")
    
    if high_count == 0 and medium_count == 0 and low_count > 0:
        summary_lines.append(f"🟢 Low Risk: {low_count} minor {'update' if low_count == 1 else 'updates'} with minimal system impact")
    
    # Add scope summary
    if total_files > 0:
        scope = f"Scope: {total_files} file{'s' if total_files != 1 else ''} affected in this change"
        summary_lines.append(scope)
    
    return summary_lines

def run_agent_with_ai():
    """Run the ExecDiff Git AI assessment with AI analysis."""
    print("\n" + "="*30)
    print("📊 File Change Assessment")
    print("="*30)
    
    diff = get_git_diff()
    
    if not diff or diff == "No git repository found or no changes detected.":
        print("(No changes detected)")
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
            print(format_table_row(symbol['name'], change_desc, symbol['risk']))
    
    print()
    
    # AI Impact Assessment Section
    if symbols:
        print("="*80)
        print("🤖 AI Impact Assessment")
        print("="*80)
        
        ai_analysis = analyze_with_ollama(diff, symbols)
        
        # Extract and display business-facing summary
        summary = extract_change_summary(ai_analysis, file_stats, symbols)
        if summary:
            print("\n📋 What Changed:")
            for line in summary:
                print(f"  {line}")
            print()
        
        print("Detailed Analysis:\n")
        print(ai_analysis)
        
        # Check for HIGH impact symbols and add warning
        high_impact_count = ai_analysis.count("Impact: HIGH")
        if high_impact_count > 0:
            print("\n⚠️  ALERT: " + str(high_impact_count) + " critical " + ("change" if high_impact_count == 1 else "changes") + " detected!")
            print("Please review carefully before deploying to production.\n")
    
    print("✅ Assessment complete!\n")
