"""
LLM provider selection component
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from utils.api_client import api_client
from pathlib import Path

class LLMSelector:
    
    def render(self) -> Dict[str, Any]:
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
        
        # Create two columns for configuration
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Provider selection
            selected_provider = st.selectbox(
                "LLM Provider",
                options=providers,
                help="Select the language model to use for evaluation",
                key="llm_provider_selector"
            )
            
            # Temperature setting
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.1,
                step=0.1,
                help="Controls randomness in model responses. Lower values = more deterministic",
                key="temperature_slider"
            )
        
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
        
        return {
            "selected_provider": selected_provider,
            "temperature": temperature,
            "verbose": verbose
        }

# Global instance
llm_selector = LLMSelector()