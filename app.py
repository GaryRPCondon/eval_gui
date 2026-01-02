"""
Main Streamlit application for AI Agent Evaluation Platform GUI
Refined version with Wizard navigation and Wide layout
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
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "setup"
    
    # Sidebar Navigation
    with st.sidebar:
        st.title(PAGE_TITLE)
        st.markdown("---")
        
        # Custom CSS to fix sidebar width and ensure buttons are full width
        st.markdown(f"""
        <style>
        /* Disable sidebar resizing and set fixed width */
        section[data-testid="stSidebar"] {{
            width: 250px !important;
            min-width: 250px !important;
            max-width: 250px !important;
        }}
        section[data-testid="stSidebar"] > div {{
            width: 250px !important;
            min-width: 250px !important;
            max-width: 250px !important;
        }}
        /* Hide the resize handle */
        section[data-testid="stSidebar"] button[kind="header"] {{
            display: none !important;
        }}
        /* Ensure buttons are full width with consistent sizing */
        div[data-testid="stSidebar"] div.stButton {{
            width: 100% !important;
        }}
        div[data-testid="stSidebar"] div.stButton > button {{
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        /* Force primary buttons to match secondary button width */
        div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }}
        /* Highlight active button with subtle background */
        button[data-testid="baseButton-secondary"]:has(p:contains("{'Setup' if st.session_state.current_page == 'setup' else 'Monitor' if st.session_state.current_page == 'monitor' else 'Results'}")) {{
            background-color: rgba(28, 131, 225, 0.1) !important;
            border-left: 3px solid rgb(28, 131, 225) !important;
        }}
        /* Make Start Evaluation button green */
        .main button[data-testid="baseButton-primary"] {{
            background-color: #4CAF50 !important;
            border-color: #4CAF50 !important;
            color: white !important;
        }}
        .main button[data-testid="baseButton-primary"]:hover {{
            background-color: #45A049 !important;
            border-color: #45A049 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Navigation buttons - all same type for consistent sizing
        if st.button("Setup", key="nav_setup", use_container_width=True):
            st.session_state.current_page = "setup"
            st.rerun()
            
        if st.button("Monitor", key="nav_monitor", use_container_width=True):
            st.session_state.current_page = "monitor"
            st.rerun()
            
        if st.button("Results", key="nav_results", use_container_width=True):
            st.session_state.current_page = "results"
            st.rerun()
            
        st.markdown("---")
        st.markdown("### Status")
        # Ensure state is initialized before checking
        execution_monitor._init_state()
        if execution_monitor.is_running:
            st.info("Running...")
        else:
            st.success("Ready")

    # Main Content Area
    if st.session_state.current_page == "setup":
        render_setup_page()
    elif st.session_state.current_page == "monitor":
        render_monitor_page()
    elif st.session_state.current_page == "results":
        render_results_page()

def render_setup_page():
    st.header("Evaluation Setup")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Scenario selection
        scenario_config = scenario_browser.render()
    
    with col2:
        # LLM configuration (pass scenario selection state)
        scenario_selected = scenario_config.get("selected_scenario") is not None
        llm_config = llm_selector.render(scenario_selected)
    
    # Store configuration in session state
    st.session_state.scenario_config = scenario_config
    st.session_state.llm_config = llm_config
    
    st.divider()
    
    # Action Bar - centered button with fixed width
    scenario_selected = scenario_config.get("selected_scenario") is not None
    llm_selected = llm_config.get("selected_provider") is not None
    
    # Add CSS for green button (same as was in llm_selector)
    st.markdown("""
    <style>
    .stButton > button[kind="primary"] {
        background-color: #4CAF50 !important;
        border-color: #4CAF50 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #45A049 !important;
        border-color: #45A049 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create centered column layout for button
    col_left, col_center, col_right = st.columns([1, 1, 1])
    
    with col_center:
        if scenario_selected and llm_selected:
            if st.button("Start Evaluation", type="primary", use_container_width=True, key="start_eval_main"):
                # Set flag to auto-start in monitor page
                st.session_state.start_execution = True
                # Switch to monitor page
                st.session_state.current_page = "monitor"
                st.rerun()
        else:
            st.warning("Please select both a Scenario and an LLM Provider to proceed.")

def render_monitor_page():
    st.header("Evaluation Monitoring")
    
    # Get configuration from session state
    scenario_config = st.session_state.get('scenario_config', {})
    llm_config = st.session_state.get('llm_config', {})
    
    # Execution interface
    execution_monitor.render(scenario_config, llm_config, hide_config=False)

def render_results_page():
    st.header("Results Analysis")
    results_viewer.render()

if __name__ == "__main__":
    main()
