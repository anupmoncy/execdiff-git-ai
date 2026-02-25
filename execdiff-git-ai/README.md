# ExecDiff Git AI

AI Impact Assessment for git changes - understand what your AI copilot changed before you commit it.

## Overview

ExecDiff Git AI is a Python CLI tool that helps developers understand the scope and implications of code changes made by AI coding assistants (like GitHub Copilot, Cursor, or Replit AI) by analyzing git diffs and extracting modified symbols (functions, classes, variables). It can optionally use a local LLM (Ollama) to assess the business impact of each change.

## Privacy

ExecDiff Git AI runs **entirely locally**.

- ✅ No code is uploaded
- ✅ No cloud calls required
- ✅ No telemetry
- ✅ Works offline with optional local LLM (Ollama)
- ✅ All analysis happens on your machine

## Features

- **Local-first**: Runs entirely on your machine with no cloud calls or telemetry
- **Impact Assessment**: Detects specific changes to functions, classes, and variables and provides human-readable summaries
- **Two modes**: Fast analysis (non-AI) or deep AI-powered analysis (optional)
- **Automatic Ollama**: AI mode automatically starts Ollama in the background - no manual setup needed
- **CLI-first**: `execdiff-git scan` and `execdiff-git scan-ai`
- **Works offline**, no telemetry

## Installation

### Prerequisites (Required)

- Python 3.8+
- Git

### Initial Setup

Install from PyPI:

```bash
pip install execdiff-git-ai
```

That's it! You can now use the non-AI mode immediately.

## How to Use

### Quick Start (No AI Required)

1. **Make your code change** (or let your AI copilot make changes)

2. **Stage your changes with git**

   ```bash
   git add .
   # For new files, you may need:
   git add -N .
   ```

3. **Run the assessment**

   ```bash
   execdiff-git scan
   ```

**Note**: For newly created files, you must run `git add -N .` (intent-to-add) so that `execdiff-git scan` can detect them. This is a git limitation for diff tools.

### AI-Powered Assessment (Optional)

**Ollama is completely optional.** The non-AI mode works great for most use cases.

If you want AI-powered analysis:

#### Option 1: Automatic (Recommended)

Simply run:

```bash
execdiff-git scan-ai
```

**ExecDiff Git AI will automatically:**
- ✅ Check if Ollama is installed
- ✅ Start Ollama server in the background
- ✅ Run AI analysis on your code changes
- ✅ Stop Ollama server when done

No manual setup needed! Everything happens automatically within the command.

#### Option 2: Manual Setup (Optional)

If you want to run Ollama manually or configure it yourself:

**Install Ollama:**

**macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Or use Homebrew (macOS):**
```bash
brew install ollama
```

**Or download from:** https://ollama.ai/

**Start the server manually (optional):**
```bash
ollama serve
```

**Then run AI mode:**
```bash
execdiff-git scan-ai
```

## Usage

### Basic Commands

**Non-AI mode (fast, always available):**
```bash
execdiff-git scan
```

**AI mode (automatic, optional):**
```bash
execdiff-git scan-ai
```

### Example Output

**Non-AI Mode:**

```
==============================
📊 File Change Assessment
==============================
File                            +Lines  -Lines
------------------------------------------------
shopping_cart.py                     10       2
checkout.py                           7       1
email/notifications.py                5       0

--------------------------------

================================================================================
📋 Impact Summary
================================================================================
Symbol                    Change Type          Risk    
--------------------------------------------------------
add_to_cart               function added       LOW     
remove_from_cart          function modified    LOW     
checkout                  function modified    LOW     
send_order_email          function added       LOW     

✅ Assessment complete!
```

**AI Mode (with Automatic Ollama):**

```
==============================
📊 File Change Assessment
==============================
File                            +Lines  -Lines
------------------------------------------------
shopping_cart.py                     10       2
checkout.py                           7       1
email/notifications.py                5       0

--------------------------------

================================================================================
📋 Impact Summary
================================================================================
Symbol                    Change Type          Risk    
--------------------------------------------------------
add_to_cart               function added       LOW     
remove_from_cart          function modified    LOW     
checkout                  function modified    LOW     
send_order_email          function added       LOW     

================================================================================
🤖 AI Impact Assessment
================================================================================

🚀 Starting Ollama server...
⏳ Waiting for Ollama server to start...
✅ Ollama server is ready!

📋 What Changed:
  🔴 Critical: Checkout now supports Apple Pay, Google Pay, and PayPal in addition to credit cards. Payment processing and customer purchase experience are directly affected.
  🟡 Important: Cart logic now merges duplicate items and updates product quantities. User experience may be impacted.
  🟢 Low Risk: Order confirmation emails improved.

  Scope: 3 files affected in this change

Detailed Analysis:

File: shopping_cart.py - Symbol: add_to_cart
Impact: LOW
Summary: Cart logic updated to better handle product quantities and merging duplicate items.

File: shopping_cart.py - Symbol: remove_from_cart
Impact: LOW
Summary: Improved item removal to prevent accidental deletion of unrelated products.

File: checkout.py - Symbol: checkout
Impact: HIGH
Summary: Checkout flow changed to support Apple Pay, Google Pay, PayPal, and credit cards.

File: email/notifications.py - Symbol: send_order_email
Impact: LOW
Summary: Confirmation emails are now sent after every successful order.

⚠️  ALERT: 1 critical change detected!
Please review carefully before deploying to production.

🛑 Ollama server stopped

✅ Assessment complete!
```

## How It Works

1. **Reads git diff** - Gets all staged and unstaged changes
2. **Extracts symbols** - Finds functions, classes, and variables
3. **Detects change type** - Identifies what kind of change was made
4. **Assesses impact** - Uses local AI (Ollama) if available, or quick heuristics
5. **Generates business summary** - Specific, non-technical impact summary (AI mode only)
6. **Advisory warnings** - Critical impact changes trigger warnings (AI mode only)

### Non-AI Mode
- Fast, always works
- No dependencies beyond git
- Detects changed symbols and file statistics
- Good for quick checks

### AI Mode
- Optional, requires Ollama to be installed
- Automatically starts and stops Ollama
- Deep analysis with business-facing summaries
- Specific details about what changed and why it matters
- No need to manually manage Ollama

## Development

Install in editable mode:

```bash
git clone https://github.com/yourusername/execdiff-git-ai.git
cd execdiff-git-ai
pip install -e .
```

Run the CLI:

```bash
execdiff-git scan
```

## Programmatic Usage

You can also use ExecDiff Git AI as a library:

```python
from execdiff_git_ai.agent import run_agent, run_agent_with_ai

# Non-AI mode (default)
run_agent()

# AI-powered mode (optional, automatically manages Ollama)
run_agent_with_ai()
```

## License

Apache-2.0

## Author

Anup Moncy (n93181165@gmail.com)

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

**Note**: This is an early-stage project. The API and behavior are subject to change.
