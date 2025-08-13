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
    
    # Remove custom CSS - use native Streamlit sidebar behavior
    pass
    
    # Application header
    st.title(PAGE_TITLE)
    st.markdown("Research platform for evaluating AI agent bias using comparative methodology")
    
    
    # Initialize session state for tab management
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Create main navigation
    tab1, tab2, tab3 = st.tabs(["Setup", "Evaluation Monitoring", "Results"])
    
    with tab1:
        st.header("Evaluation Setup")
        
        # Scenario selection
        scenario_config = scenario_browser.render()
        
        st.divider()
        
        # LLM configuration (pass scenario selection state)
        scenario_selected = scenario_config.get("selected_scenario") is not None
        llm_config = llm_selector.render(scenario_selected)
        
        # Store configuration in session state
        st.session_state.scenario_config = scenario_config
        st.session_state.llm_config = llm_config
        
        # Clean interface - no debug clutter
        
        # Pass execution control to LLM selector
        scenario_selected = scenario_config.get("selected_scenario") is not None
        llm_selected = llm_config.get("selected_provider") is not None
        
        # Show warning if missing selections
        if not scenario_selected or not llm_selected:
            missing = []
            if not scenario_selected:
                missing.append("scenario")
            if not llm_selected:
                missing.append("LLM provider")
            
            st.warning(f"Please select a {' and '.join(missing)} to enable evaluation")
    
    with tab2:
        st.header("Evaluation Monitoring")
        
        # Get configuration from session state
        scenario_config = st.session_state.get('scenario_config', {})
        llm_config = st.session_state.get('llm_config', {})
        
        # Add an invisible refresh button that auto-clicks when tab loads
        # This creates the effect of refreshing the tab content
        if 'monitoring_tab_loaded' not in st.session_state:
            st.session_state.monitoring_tab_loaded = True
            # Small invisible element that triggers update
            st.empty()
        
        # Add manual refresh option for user
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 Refresh", key="refresh_monitoring_tab", help="Refresh monitoring data"):
                pass  # Button click triggers refresh
        
        # Execution interface (simplified - no configuration display)  
        # Let the execution monitor handle the start_execution flag
        execution_status = execution_monitor.render(scenario_config, llm_config, hide_config=True)
    
    with tab3:
        st.header("Results")
        
        # Results display
        results_viewer.render()
    

if __name__ == "__main__":
    main()