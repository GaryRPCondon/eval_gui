"""
Scenario browser component for selecting and viewing evaluation scenarios
"""

import streamlit as st
import json
from typing import Dict, Any, List, Optional
from utils.file_manager import file_manager
from utils.data_formatter import data_formatter

class ScenarioBrowser:
    
    def render(self) -> Dict[str, Any]:
        """Render scenario selection and details"""
        
        st.header("Scenario Selection")
        
        # Get available scenarios
        try:
            scenarios = file_manager.get_scenarios_list()
        except Exception as e:
            st.error(f"Failed to load scenarios: {e}")
            return {"selected_scenario": None}
        
        if not scenarios:
            st.warning("No scenarios found in the scenarios directory")
            return {"selected_scenario": None}
        
        # Create scenario selection
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Filter by type
            scenario_types = list(set([s["type"] for s in scenarios]))
            selected_type = st.selectbox(
                "Scenario Type",
                options=["All"] + scenario_types,
                help="Filter scenarios by type",
                key="scenario_type_filter"
            )
            
            # Filter scenarios
            filtered_scenarios = scenarios
            if selected_type != "All":
                filtered_scenarios = [s for s in scenarios if s["type"] == selected_type]
            
            # Scenario selection dropdown
            scenario_options = [f"{s['name']} ({s['type']})" for s in filtered_scenarios]
            if not scenario_options:
                st.warning("No scenarios match the selected filter")
                return {"selected_scenario": None}
            
            selected_index = st.selectbox(
                "Select Scenario",
                options=range(len(scenario_options)),
                format_func=lambda x: scenario_options[x] if x < len(scenario_options) else "",
                help="Choose an evaluation scenario to run",
                key="scenario_selector"
            )
            
            selected_scenario = filtered_scenarios[selected_index] if selected_index < len(filtered_scenarios) else None
        
        with col2:
            if selected_scenario:
                # Display scenario summary
                st.subheader("Scenario Summary")
                summary_data = {
                    "Name": selected_scenario["name"],
                    "Type": selected_scenario["type"],
                    "Description": selected_scenario["description"]
                }
                for key, value in summary_data.items():
                    st.text(f"{key}: {value}")
        
        # Scenario details section
        if selected_scenario:
            with st.expander("View Scenario Details", expanded=False):
                self._render_scenario_details(selected_scenario)
        
        return {
            "selected_scenario": selected_scenario,
            "scenario_data": self._load_scenario_data(selected_scenario) if selected_scenario else None
        }
    
    def _render_scenario_details(self, scenario: Dict[str, Any]):
        """Render detailed scenario information"""
        try:
            # Load full scenario data
            scenario_data = file_manager.read_scenario(scenario["id"])
            if not scenario_data:
                st.error("Failed to load scenario details")
                return
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Overview", "JSON Tree", "Raw JSON"])
            
            with tab1:
                # Formatted overview
                formatted_data = data_formatter.format_scenario_for_display(scenario_data)
                for key, value in formatted_data.items():
                    if isinstance(value, list):
                        st.text(f"{key}:")
                        for item in value:
                            st.text(f"  • {item}")
                    else:
                        st.text(f"{key}: {value}")
            
            with tab2:
                # Tree view of JSON structure
                tree_display = data_formatter.format_json_for_tree_display(scenario_data)
                st.code(tree_display, language="json")
            
            with tab3:
                # Raw JSON view
                st.json(scenario_data)
                
        except Exception as e:
            st.error(f"Error displaying scenario details: {e}")
    
    def _load_scenario_data(self, scenario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Load full scenario data for execution"""
        if not scenario:
            return None
        
        try:
            return file_manager.read_scenario(scenario["id"])
        except Exception as e:
            st.error(f"Failed to load scenario data: {e}")
            return None

# Global instance
scenario_browser = ScenarioBrowser()