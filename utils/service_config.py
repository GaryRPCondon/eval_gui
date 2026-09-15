"""
Off-disk access to the evaluation service's configuration modules.

The GUI must not import agent_eval_service as a package (different working
directory, different dependencies), so llm_providers.py and
agent_frameworks.py are loaded by path, once per Streamlit server process.
Editing either file therefore needs "Clear cache" (or a restart) to show up.
"""

import importlib.util
from types import ModuleType

import streamlit as st

from config.settings import SERVICE_CONFIG_PATH


@st.cache_resource(show_spinner=False)
def load_service_module(name: str) -> ModuleType:
    path = SERVICE_CONFIG_PATH / f"{name}.py"
    if not path.is_file():
        raise FileNotFoundError(f"Service config module not found: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def llm_providers() -> ModuleType:
    return load_service_module("llm_providers")


def agent_frameworks() -> ModuleType:
    return load_service_module("agent_frameworks")


def available_models() -> list:
    """Model aliases the agents accept (same list FastAPI's /llm-providers returns)."""
    return list(llm_providers().get_available_models())


def provider_config(model_name: str) -> dict:
    return llm_providers().get_provider_config(model_name) or {}


def provider_supports_temperature(model_name: str) -> bool:
    """Single source of truth for temperature support: the supports_temperature flag in llm_providers.py."""
    return bool(provider_config(model_name).get("supports_temperature", True))
