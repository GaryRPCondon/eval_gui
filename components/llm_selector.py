"""
LLM provider selection component
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from utils.api_client import api_client
from pathlib import Path

class LLMSelector:
    
    def render(self, scenario_selected: bool = False) -> Dict[str, Any]:
        """Render LLM provider selection interface"""
        
        st.header("Model Configuration")
        
        # Get available providers from evaluation service API
        providers = api_client.get_llm_providers()
        
        if not providers:
            st.warning("No LLM providers available")
            return {"selected_provider": None, "temperature": 0.1, "verbose": False}
        
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
            
            # Temperature setting - check support for currently selected provider
            temperature_options = [round(x * 0.1, 1) for x in range(0, 21)]  # 0.0 to 2.0 in 0.1 steps
            
            # Check if selected provider supports temperature (reactive to selection change)
            provider_supports_temp = True  # Default
            help_text = "Controls randomness in model responses. Lower values = more deterministic"
            
            if selected_provider:  # Only check if a provider is selected
                # Hard-coded temperature support info (more reliable than dynamic import)
                models_without_temp_support = {
                    "openai-gpt5", 
                    "openai-gpt5-mini", 
                    "openai-gpt5-nano"
                }
                
                provider_supports_temp = selected_provider not in models_without_temp_support
                
                if not provider_supports_temp:
                    help_text = "⚠️ This model does not support temperature parameter. Model default will be used."
            
            temperature = st.selectbox(
                "Temperature",
                options=temperature_options,
                index=1,  # Default to 0.1 (second item in list)
                help=help_text,
                key="temperature_selector",
                disabled=not provider_supports_temp  # Disable if not supported
            )
            
            # Show additional warning for unsupported models
            if selected_provider and not provider_supports_temp:
                st.caption("🚫 Temperature control disabled for this model")
        
        with col2:
            # Verbose mode toggle
            verbose = st.checkbox(
                "Verbose Mode",
                value=True,
                help="Enable detailed logging during evaluation execution",
                key="verbose_checkbox"
            )
            
            # Display provider information
            if selected_provider:
                st.subheader("Model Information")
                # Try to get more details about the selected provider
                # Model information from centralized service config
                import importlib.util
                llm_providers_path = Path(__file__).parent.parent.parent / "agent_eval_service" / "config" / "llm_providers.py"
                spec = importlib.util.spec_from_file_location("llm_providers", llm_providers_path)
                llm_providers_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(llm_providers_module)
                get_provider_config = llm_providers_module.get_provider_config
                
                provider_config = get_provider_config(selected_provider)
                if provider_config:
                    st.text(f"Model: {provider_config['model']}")
                    st.text(f"Provider: {selected_provider}")
                    st.text(f"Temperature Support: {'Yes' if provider_config.get('supports_temperature', True) else 'No'}")
                else:
                    st.text(f"Provider: {selected_provider}")
        
        return {
            "selected_provider": selected_provider,
            "temperature": temperature,
            "verbose": verbose
        }

# Global instance
llm_selector = LLMSelector()