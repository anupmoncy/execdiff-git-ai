"""
ExecDiff Git AI - Analyze AI-driven code changes.

This package provides tools to analyze Git diffs and assess the impact
of changes made by AI coding assistants.
"""

__version__ = "1.0.2"
__author__ = "Anup Moncy"

try:
    from execdiff_git_ai.agent import run_agent, run_agent_with_ai
    __all__ = ['run_agent', 'run_agent_with_ai']
except ImportError as e:
    print(f"Warning: Could not import agent functions: {e}")
    __all__ = []
