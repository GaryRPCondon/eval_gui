"""
Main Streamlit application for AI Agent Evaluation Platform GUI
"""

import streamlit as st
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from components.scenario_browser import scenario_browser
from components.llm_selector import llm_selector
from components.execution_monitor import execution_monitor
from components.results_viewer import results_viewer

def main():
    """Main application entry point"""
    
    # Configure page
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT
    )
    
    # Application header
    st.title(PAGE_TITLE)
    st.markdown("Research platform for evaluating AI agent bias using comparative methodology")
    
    # Create main navigation
    tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Execute", "Results", "History"])
    
    with tab1:
        st.header("Evaluation Setup")
        
        # Scenario selection
        scenario_config = scenario_browser.render()
        
        st.divider()
        
        # LLM configuration
        llm_config = llm_selector.render()
        
        # Store configuration in session state
        st.session_state.scenario_config = scenario_config
        st.session_state.llm_config = llm_config
    
    with tab2:
        st.header("Execution")
        
        # Get configuration from session state
        scenario_config = st.session_state.get('scenario_config', {})
        llm_config = st.session_state.get('llm_config', {})
        
        # Execution interface
        execution_status = execution_monitor.render(scenario_config, llm_config)
    
    with tab3:
        st.header("Results")
        
        # Results display
        results_viewer.render()
    
    with tab4:
        # Use separate history render method
        results_viewer.render_history()
    
    # Sidebar information
    with st.sidebar:
        st.header("System Information")
        
        # Service status check
        try:
            from utils.api_client import api_client
            providers = api_client.get_llm_providers()
            st.success("Evaluation service: Connected")
            st.text(f"Available providers: {len(providers)}")
        except Exception:
            st.error("Evaluation service: Disconnected")
            st.text("Make sure the service is running on localhost:8000")
        
        st.divider()
        
        # Quick help
        st.subheader("Quick Start")
        st.markdown("""
        1. **Setup**: Select scenario and model
        2. **Execute**: Run the evaluation 
        3. **Results**: View analysis and reports
        
        **Requirements:**
        - Evaluation service running on port 8000
        - Agent execution environment configured
        """)
        
        st.divider()
        
        # System paths info
        with st.expander("System Paths"):
            from config.settings import EVAL_SERVICE_PATH, SCENARIOS_PATH, RESULTS_PATH
            st.text(f"Service: {EVAL_SERVICE_PATH}")
            st.text(f"Scenarios: {SCENARIOS_PATH}")
            st.text(f"Results: {RESULTS_PATH}")

if __name__ == "__main__":
    main()