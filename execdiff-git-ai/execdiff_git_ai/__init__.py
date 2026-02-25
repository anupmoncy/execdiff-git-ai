"""
ExecDiff Git AI - Local-first tool for analyzing AI-driven code changes.

This package provides tools to analyze Git diffs and assess the impact
of changes made by AI coding assistants.
"""

__version__ = "1.0.0"
__author__ = "Anup Moncy"

from execdiff_git_ai.agent import run_agent, run_agent_with_ai

__all__ = ["run_agent", "run_agent_with_ai"]
