"""
GUI configuration settings
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BASE_DIR.parent
EVAL_SERVICE_PATH = PROJECT_ROOT / "agent_eval_service"
LANGGRAPH_AGENT_PATH = PROJECT_ROOT / "langgraph_agent"

# API settings
API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-1234"

# File system paths
SCENARIOS_PATH = EVAL_SERVICE_PATH / "scenarios"
RESULTS_PATH = EVAL_SERVICE_PATH / "results"
REPORTS_PATH = RESULTS_PATH / "eval_reports"
RESEARCH_RESULTS_CSV = RESULTS_PATH / "research_results.csv"

# Agent execution settings
AGENT_WORKING_DIR = LANGGRAPH_AGENT_PATH
SINGLE_AGENT_SCRIPT = "agent.py"
PAROLE_BOARD_AGENT_SCRIPT = "parole_board_agent.py"
MEDICAL_MULTI_AGENT_SCRIPT = "medical_resume_evaluator.py"
CONTROL_PAROLE_AGENT_SCRIPT = "control_parole_board_agent.py"

# GUI settings
PAGE_TITLE = "AI Agent Evaluation Platform"
PAGE_ICON = "🧪"
LAYOUT = "centered"

# Default values
DEFAULT_VERBOSE = False
DEFAULT_TIMEOUT = 300  # 5 minutes