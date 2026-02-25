# ExecDiff Git AI

AI Impact Assessment for git changes - understand what your AI copilot changed before you commit it.

## Intro

ExecDiff Git AI is a Python CLI tool that helps developers understand the scope and implications of code changes made by AI coding assistants (like GitHub Copilot, Cursor, or Replit AI). It analyzes git diffs and extracts modified symbols (functions, classes, variables).

**100% Local - No Cloud Required**
- ✅ No code is uploaded
- ✅ No cloud calls required
- ✅ No telemetry
- ✅ Works offline with optional local LLM (Ollama)
- ✅ All analysis happens on your machine

## Features & Privacy

- **Local-first**: Runs entirely on your machine with no cloud calls or telemetry
- **Fast Assessment**: Quick symbol detection and impact analysis (always available)
- **Optional AI Mode**: Deep business-facing analysis using local Ollama (opt-in)
- **CLI-first**: Simple commands `execdiff-git assess` and `execdiff-git ai-assess`
- **Zero Dependencies**: Non-AI mode works with just Python and Git
- **Privacy-focused**: No data sent to external servers

## Installation

### Prerequisites (Required)

- Python 3.8+
- Git

### Install Package

```bash
pip install execdiff-git-ai
```

### Optional: Ollama for AI Mode

For AI-powered analysis, optionally install:

| Component | Size | Purpose |
|-----------|------|---------|
| Ollama | ~50MB | Local AI runtime |
| tinyllama model | ~637MB | AI analysis model |

**Total: ~700MB (one-time, optional)**

**Install Ollama:**

macOS:
```bash
brew install ollama
```

macOS/Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Or download from: https://ollama.ai/

---

## Initial Setup

1. **Make your code change** (or let your AI copilot make changes)

2. **Stage your changes with git**

   ```bash
   git add .
   # For new files, you may need:
   git add -N .
   ```

3. **You're ready to use ExecDiff Git AI!**

---

## Quick Assessment (No AI)

Fast, local symbol detection - no setup required.

### Usage

```bash
execdiff-git assess
```

### Example Output

```
==============================
📊 File Change Assessment
==============================
File                            +Lines  -Lines
------------------------------------------------
test_feature.py                     14       0

--------------------------------

================================================================================
📋 Impact Summary
================================================================================
Symbol                    Change Type          Impact
--------------------------------------------------------
[NEW] authenticate_user   function added       LOW
[NEW] create_session      function added       LOW
[NEW] validate_token      function added       LOW

✅ Assessment complete!
```

---

## AI-Powered Assessment

Deep analysis with business-facing summaries using local Ollama (requires optional Ollama installation).

### Usage

```bash
execdiff-git ai-assess
```

The tool will:
- Check if Ollama is installed
- Ask permission before downloading AI model (~637MB)
- Start Ollama server automatically
- Analyze each change individually
- Get overall business impact summary
- Stop Ollama server when done

### Example Output

```
==============================
📊 File Change Assessment
==============================
File                            +Lines  -Lines
------------------------------------------------
test_feature.py                     14       0

--------------------------------

================================================================================
📋 Impact Summary
================================================================================
Symbol                    Change Type          Impact
--------------------------------------------------------
[NEW] authenticate_user   function added       LOW
[NEW] create_session      function added       LOW
[NEW] validate_token      function added       LOW

================================================================================
🤖 AI Impact Assessment
================================================================================

🚀 Starting Ollama server...
⏳ Waiting for Ollama server to start...
✅ Ollama server is ready!

🧠 Analyzing 3 changes:

  • [NEW] authenticate_user... ✓
    Handles user login and credential verification.

  • [NEW] create_session... ✓
    Establishes user sessions after authentication.

  • [NEW] validate_token... ✓
    Verifies tokens are valid and not expired.

  • Overall impact... ✓

Overall:
• System now provides complete authentication workflow with secure token validation.

Changes:
• [NEW] authenticate_user: Handles user login and credential verification.
• [NEW] create_session: Establishes user sessions after authentication.
• [NEW] validate_token: Verifies tokens are valid and not expired.

🛑 Ollama server stopped

✅ Assessment complete!
```

---

## Symbol Change Types

Each symbol is labeled with its change type:

- **[NEW]** - Newly added function or class
- **[MODIFIED]** - Existing function or class that was changed
- **[DELETED]** - Function or class that was removed

---

## How It Works

1. **Reads git diff** - Gets all staged changes
2. **Extracts symbols** - Finds functions, classes, and variables
3. **Detects changes** - Identifies NEW, MODIFIED, or DELETED code
4. **Analyzes impact** - AI provides business-facing summaries (AI mode only)

## Development

```bash
git clone https://github.com/anupmoncy/execdiff-git-ai.git
cd execdiff-git-ai
pip install -e .
execdiff-git assess
```

## Library Usage

```python
from execdiff_git_ai.agent import run_agent, run_agent_with_ai

# Non-AI mode
run_agent()

# AI mode
run_agent_with_ai()
```

## License

Apache-2.0

## Author

Anup Moncy (n93181165@gmail.com)

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

**Note**: Early-stage project. API and behavior subject to change.
