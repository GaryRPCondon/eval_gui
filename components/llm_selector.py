"""
LLM provider selection component
"""

import streamlit as st
from typing import Dict, Any
from utils.api_client import api_client
from utils import service_config
from config.settings import DEFAULT_TEMPERATURE, DEFAULT_VERBOSE

class LLMSelector:

    def render(self, scenario_selected: bool = False) -> Dict[str, Any]:
        """Render LLM provider selection interface"""

        st.header("Model Configuration")

        # Provider list: evaluation service API first, llm_providers.py on disk as fallback (same list)
        providers = api_client.get_llm_providers()
        source_note = None
        if not providers:
            try:
                providers = service_config.available_models()
                source_note = "Evaluation service API unreachable; provider list loaded from llm_providers.py"
            except Exception as e:
                st.error(f"No LLM providers available: {e}")
                return {"selected_provider": None, "temperature": DEFAULT_TEMPERATURE, "verbose": DEFAULT_VERBOSE}

        if not providers:
            st.warning("No LLM providers available")
            return {"selected_provider": None, "temperature": DEFAULT_TEMPERATURE, "verbose": DEFAULT_VERBOSE}

        # Sort providers alphabetically
        providers_sorted = sorted(providers)

        # Create two columns for configuration
        col1, col2 = st.columns([2, 3])

        with col1:
            # Provider selection
            selected_provider = st.selectbox(
                "LLM Provider",
                options=providers_sorted,
                help="Select the language model to use for evaluation",
                key="llm_provider_selector"
            )
            if source_note:
                st.caption(source_note)

            # Temperature setting - support comes from the provider's supports_temperature flag
            temperature_options = [round(x * 0.1, 1) for x in range(0, 21)]  # 0.0 to 2.0 in 0.1 steps

            provider_supports_temp = True
            help_text = "Controls randomness in model responses. Lower values = more deterministic"
            if selected_provider:
                provider_supports_temp = service_config.provider_supports_temperature(selected_provider)
                if not provider_supports_temp:
                    help_text = "⚠️ This model does not support temperature parameter. Model default will be used."

            temperature = st.selectbox(
                "Temperature",
                options=temperature_options,
                index=temperature_options.index(DEFAULT_TEMPERATURE),
                help=help_text,
                key="temperature_selector",
                disabled=not provider_supports_temp
            )

            if selected_provider and not provider_supports_temp:
                st.caption("🚫 Temperature control disabled for this model")

        with col2:
            # Verbose mode toggle
            verbose = st.checkbox(
                "Verbose Mode",
                value=DEFAULT_VERBOSE,
                help="Enable detailed logging during evaluation execution",
                key="verbose_checkbox"
            )

            # Display provider information from the centralized service config
            if selected_provider:
                st.subheader("Model Information")
                provider_config = service_config.provider_config(selected_provider)
                if provider_config:
                    st.text(f"Model: {provider_config.get('model', 'unknown')}")
                    st.text(f"Provider: {selected_provider}")
                    st.text(f"Temperature Support: {'Yes' if provider_supports_temp else 'No'}")
                else:
                    st.text(f"Provider: {selected_provider}")

        return {
            "selected_provider": selected_provider,
            "temperature": temperature,
            "verbose": verbose
        }

# Global instance
llm_selector = LLMSelector()
