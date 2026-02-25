# ExecDiff Git AI

AI Impact Assessment for git changes - understand what your AI copilot changed before you commit it.

## Overview

ExecDiff Git AI is a Python CLI tool that helps developers understand the scope and implications of code changes made by AI coding assistants (like GitHub Copilot, Cursor, or Replit AI) by analyzing git diffs and extracting modified symbols (functions, classes, variables). It can optionally use a local LLM (Ollama) to assess the risk of each change.

## Privacy

ExecDiff Git AI runs **entirely locally**.

- ✅ No code is uploaded
- ✅ No cloud calls required
- ✅ No telemetry
- ✅ Works offline with local LLM (Ollama)
- ✅ All analysis happens on your machine

## Features

- **Local-first**: Runs entirely on your machine with no cloud calls or telemetry
- **Impact Assessment**: Detects specific changes to functions, classes, and variables and provides human-readable summaries
- **AI-powered risk assessment**: Utilizes local Ollama for intelligent impact analysis and scoring (optional)
- **CLI-first**: `execdiff-git scan` and `execdiff-git scan-ai`
- **Works offline**, no telemetry

## Installation

### Prerequisites

- Python 3.8+
- Git
- Ollama (optional, for AI risk assessment)

### Initial Setup

Install from PyPI:

```bash
pip install execdiff-git-ai
```

## How to Use

1. **Make your code change** (or let your AI copilot make changes)

2. **Stage your changes with git**

   ```bash
   git add .
   # For new files, you may need:
   git add -N .
   ```

3. **Run the assessment (no AI)**

   ```bash
   execdiff-git scan
   ```

   Or, to use AI-powered risk assessment (requires Ollama):

   ```bash
   execdiff-git scan-ai
   ```

**Note**: For newly created files, you must run `git add -N .` (intent-to-add) so that `execdiff-git scan` or `execdiff-git scan-ai` can detect them. This is a git limitation for diff tools.

## Usage

### Basic Commands

Analyze changes in the current repository:

```bash
execdiff-git scan
```

Analyze with AI-powered risk assessment:

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
Symbol                    Change Type          Impact  
--------------------------------------------------------
add_to_cart               function modified    MEDIUM  
remove_from_cart          function modified    LOW     
checkout                  function modified    HIGH    
send_order_email          function added       LOW     

✅ Assessment complete!
```

## Optional: Install Ollama for AI Risk Assessment

Ollama enables intelligent risk scoring. Install and configure:

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or use Homebrew (macOS)
brew install ollama

# Pull the model
ollama pull llama2

# Start the server (runs on localhost:11434)
ollama serve
```

With Ollama running, you'll also get AI-powered impact assessment:

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
Symbol                    Change Type          Impact  
--------------------------------------------------------
add_to_cart               function modified    MEDIUM  
remove_from_cart          function modified    LOW     
checkout                  function modified    HIGH    
send_order_email          function added       LOW     

================================================================================
🤖 AI Impact Assessment
================================================================================

📋 What Changed:
  🔴 Critical: Checkout now supports Apple Pay, Google Pay, and PayPal in addition to credit cards, and changes the order completion flow. Payment processing reliability and customer purchase experience are directly affected.
  🟡 Important: Cart logic now merges duplicate items and updates product quantities in one step. This changes how users see totals and manage products in their cart.
  🟢 Low Risk: Order confirmation emails improved. Cart item removal is more reliable.

  Scope: 3 files modified (22 additions, 3 removals)

Detailed Analysis:

File: shopping_cart.py - Symbol: add_to_cart
Impact: MEDIUM
Summary: Cart logic updated to better handle product quantities and merging duplicate items.

File: shopping_cart.py - Symbol: remove_from_cart
Impact: LOW
Summary: Improved item removal to prevent accidental deletion of unrelated products.

File: checkout.py - Symbol: checkout
Impact: HIGH
Summary: Checkout flow changed to support Apple Pay, Google Pay, PayPal, and credit cards, and to update order completion steps.

File: email/notifications.py - Symbol: send_order_email
Impact: LOW
Summary: Confirmation emails are now sent after every successful order.

⚠️  ALERT: 1 critical change detected!
Please review carefully before deploying to production.

✅ Assessment complete!
```

## How It Works

1. **Reads git diff** - Gets all staged and unstaged changes
2. **Extracts symbols** - Finds functions, classes, and variables
3. **Detects change type** - Identifies what kind of change was made
4. **Assesses impact** - Uses local AI (Ollama) or heuristics
5. **Generates recommendations** - Suggests testing and review actions (AI mode only)
6. **Advisory warnings** - Critical impact changes trigger warnings (AI mode only)

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

# AI-powered mode (optional, requires Ollama)
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
