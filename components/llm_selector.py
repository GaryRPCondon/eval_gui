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
        
        # Get available providers - use direct config access as fallback
        try:
            providers = api_client.get_llm_providers()
        except Exception:
            # Fallback to reading from config directly
            try:
                import sys
                import os
                # Add the langgraph_agent directory to path
                langgraph_path = str(Path(__file__).parent.parent.parent / "langgraph_agent")
                if langgraph_path not in sys.path:
                    sys.path.insert(0, langgraph_path)
                from config import LLM_CONFIGS
                providers = list(LLM_CONFIGS.keys())
            except Exception as e:
                st.error(f"Failed to load LLM providers: {e}")
                st.info("Using default provider list")
                providers = ["deepseek", "openai-gpt4o", "claude", "grok"]
        
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
                value=False,
                help="Enable detailed logging during evaluation execution",
                key="verbose_checkbox"
            )
            
            # Display provider information
            if selected_provider:
                st.subheader("Model Information")
                # Try to get more details about the selected provider
                try:
                    # Import here to avoid path issues
                    import sys
                    import os
                    # Add the langgraph_agent directory to path
                    langgraph_path = str(Path(__file__).parent.parent.parent / "langgraph_agent")
                    if langgraph_path not in sys.path:
                        sys.path.insert(0, langgraph_path)
                    from config import LLM_CONFIGS
                    
                    if selected_provider in LLM_CONFIGS:
                        config = LLM_CONFIGS[selected_provider]
                        st.text(f"Model: {config['model']}")
                        st.text(f"Provider: {selected_provider}")
                        st.text(f"Temperature Support: {'Yes' if config.get('supports_temperature', True) else 'No'}")
                    else:
                        st.text(f"Provider: {selected_provider}")
                except Exception:
                    st.text(f"Provider: {selected_provider}")
                
                # Start Evaluation button right under Model Information
                
                # Custom CSS for a nice green button with fixed width
                st.markdown("""
                <style>
                .stButton > button[kind="primary"] {
                    background-color: #4CAF50 !important;
                    border-color: #4CAF50 !important;
                    width: 150px !important;
                    max-width: 150px !important;
                }
                .stButton > button[kind="primary"]:hover {
                    background-color: #45A049 !important;
                    border-color: #45A049 !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                if scenario_selected and selected_provider:
                    if st.button("Start Evaluation", type="primary", key="start_eval_from_llm"):
                        # Set flag to start execution
                        st.session_state.start_execution = True
                        
                        st.info("**Evaluation Started** - Switch to 'Evaluation Monitoring' tab to view progress")
                else:
                    st.button("Start Evaluation", disabled=True, key="start_eval_disabled")
                    if not scenario_selected:
                        st.caption("Select a scenario first")
                    elif not selected_provider:
                        st.caption("Select an LLM provider first")
        
        return {
            "selected_provider": selected_provider,
            "temperature": temperature,
            "verbose": verbose
        }

# Global instance
llm_selector = LLMSelector()