"""
Agent framework selection component.

Reads the framework registry (agent_eval_service/config/agent_frameworks.py)
off disk and lets the user pick which agent implementation runs the
evaluation. Frameworks whose agent folder or virtual environment is missing
are listed but marked unavailable, with the reason, and the Start button is
gated on availability in app.py.
"""

import streamlit as st
from typing import Dict, Any

from utils import service_config
from config.settings import PROJECT_ROOT


class FrameworkSelector:

    def render(self) -> Dict[str, Any]:
        """Render framework selection; returns framework_config for session state."""
        try:
            registry = service_config.agent_frameworks()
        except Exception as e:
            st.error(f"Agent framework registry unavailable: {e}")
            return {"selected_framework": None, "display_name": None, "available": False, "reason": str(e)}

        framework_ids = registry.get_framework_ids()
        status = {fid: registry.check_framework(fid, PROJECT_ROOT) for fid in framework_ids}

        def label(fid: str) -> str:
            name = status[fid]["display_name"]
            return name if status[fid]["available"] else f"{name} (unavailable)"

        col1, _ = st.columns([1, 2])
        with col1:
            selected = st.selectbox(
                "Agent Framework",
                options=framework_ids,
                index=framework_ids.index(registry.DEFAULT_FRAMEWORK),
                format_func=label,
                help="Which agent implementation runs the evaluation. All frameworks call the same evaluation service.",
                key="framework_selector",
            )
            selected_status = status[selected]
            spec = registry.get_framework(selected)
            if selected_status["available"]:
                st.caption(f"Runs {spec['agent_dir']}/<scenario>.py in the {spec['venv_dir']} environment")
            else:
                st.warning(f"{selected_status['display_name']} is not available: {selected_status['reason']}")

        return {
            "selected_framework": selected,
            "display_name": selected_status["display_name"],
            "available": selected_status["available"],
            "reason": selected_status["reason"],
        }


# Global instance
framework_selector = FrameworkSelector()
