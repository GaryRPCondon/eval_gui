"""
GUI configuration settings
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BASE_DIR.parent
EVAL_SERVICE_PATH = PROJECT_ROOT / "agent_eval_service"
SERVICE_CONFIG_PATH = EVAL_SERVICE_PATH / "config"   # llm_providers.py, agent_frameworks.py (loaded off disk)

# API settings (FastAPI is optional: used for the provider list, with a disk fallback)
API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-1234"

# File system paths
SCENARIOS_PATH = EVAL_SERVICE_PATH / "scenarios"
RESULTS_PATH = EVAL_SERVICE_PATH / "results"
REPORTS_PATH = RESULTS_PATH / "eval_reports"
RESEARCH_RESULTS_CSV = RESULTS_PATH / "research_results.csv"

# GUI settings
PAGE_TITLE = "AI Agent Evaluation Platform"
PAGE_ICON = "🧪"
LAYOUT = "wide"

# Default values (must match the agents' argparse defaults so the GUI shows what runs)
DEFAULT_VERBOSE = True
DEFAULT_TEMPERATURE = 0.1
