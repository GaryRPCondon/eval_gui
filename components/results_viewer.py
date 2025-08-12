"""
Results viewer component for displaying evaluation results and reports
Pure display layer - reads calculated values from CSV and markdown files
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from utils.file_manager import file_manager
from utils.data_formatter import data_formatter

class ResultsViewer:
    
    def render(self) -> Dict[str, Any]:
        """Render results display interface"""
        
        st.header("Evaluation Results")
        
        # Load research results
        try:
            results_df = file_manager.get_research_results()
        except Exception as e:
            st.error(f"Failed to load results: {e}")
            return {"status": "error"}
        
        if results_df is None or results_df.empty:
            st.info("No evaluation results found. Run an evaluation to see results here.")
            return {"status": "no_results"}
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Latest Results", "Results History", "Detailed Reports"])
        
        with tab1:
            self._render_latest_results(results_df)
        
        with tab2:
            self._render_results_history(results_df, key_prefix="results")
        
        with tab3:
            self._render_detailed_reports()
        
        return {"status": "displayed"}
    
    def render_history(self) -> Dict[str, Any]:
        """Render history-focused interface"""
        
        st.header("Evaluation History")
        
        # Load research results
        try:
            results_df = file_manager.get_research_results()
        except Exception as e:
            st.error(f"Failed to load results: {e}")
            return {"status": "error"}
        
        if results_df is None or results_df.empty:
            st.info("No evaluation results found. Run an evaluation to see results here.")
            return {"status": "no_results"}
        
        # Render history view with different key prefix
        self._render_results_history(results_df, key_prefix="history")
        
        return {"status": "displayed"}
    
    def _render_latest_results(self, results_df: pd.DataFrame):
        """Display the most recent evaluation results"""
        
        st.subheader("Latest Evaluations")
        
        # Get the 10 most recent results
        latest_results = results_df.head(10)
        
        if latest_results.empty:
            st.info("No recent results available")
            return
        
        # Display each result as an expandable card
        for idx, (_, row) in enumerate(latest_results.iterrows()):
            formatted_summary = data_formatter.format_results_summary(row)
            
            # Create expandable result card
            with st.expander(
                f"{formatted_summary['Model']} - {formatted_summary['Scenario']} - {formatted_summary['Bias Level']} Bias",
                expanded=(idx == 0)  # Expand first result by default
            ):
                # Display key metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Bias Score", formatted_summary["Bias Score"])
                    st.metric("P-Value", formatted_summary["P-Value"])
                
                with col2:
                    st.metric("Effect Size", formatted_summary["Effect Size (Cohen's d)"])
                    st.metric("Bias Level", formatted_summary["Bias Level"])
                
                with col3:
                    st.metric("Statistical Significance", formatted_summary["Statistical Significance"])
                    if "Demographic Favored" in formatted_summary:
                        st.metric("Demographic Favored", formatted_summary["Demographic Favored"])
                
                # Additional details
                st.subheader("Detailed Information")
                for key, value in formatted_summary.items():
                    if key not in ["Bias Score", "P-Value", "Effect Size (Cohen's d)", "Bias Level", 
                                  "Statistical Significance", "Demographic Favored"]:
                        st.text(f"{key}: {value}")
    
    def _render_results_history(self, results_df: pd.DataFrame, key_prefix: str = "history"):
        """Display searchable/filterable results history"""
        
        st.subheader("Results History")
        
        # Filters - use actual values from CSV data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Model filter
            models = ["All"] + sorted(results_df["model_name"].unique().tolist())
            selected_model = st.selectbox("Model", models, key=f"{key_prefix}_model_filter")
        
        with col2:
            # Scenario filter
            scenarios = ["All"] + sorted(results_df["scenario_id"].unique().tolist())
            selected_scenario = st.selectbox("Scenario", scenarios, key=f"{key_prefix}_scenario_filter")
        
        with col3:
            # Bias level filter
            bias_levels = ["All"] + sorted(results_df["bias_level"].unique().tolist())
            selected_bias_level = st.selectbox("Bias Level", bias_levels, key=f"{key_prefix}_bias_filter")
        
        with col4:
            # Statistical significance filter - read from CSV column
            if "statistical_significance" in results_df.columns:
                # Extract unique significance values from the CSV
                significance_values = results_df["statistical_significance"].unique()
                significance_options = ["All"] + sorted([str(v) for v in significance_values if pd.notna(v)])
            else:
                significance_options = ["All"]
            selected_significance = st.selectbox("Statistical Significance", significance_options, key=f"{key_prefix}_significance_filter")
        
        # Apply filters
        filtered_df = results_df.copy()
        
        if selected_model != "All":
            filtered_df = filtered_df[filtered_df["model_name"] == selected_model]
        
        if selected_scenario != "All":
            filtered_df = filtered_df[filtered_df["scenario_id"] == selected_scenario]
        
        if selected_bias_level != "All":
            filtered_df = filtered_df[filtered_df["bias_level"] == selected_bias_level]
        
        if selected_significance != "All" and "statistical_significance" in filtered_df.columns:
            # Use string matching to filter by the calculated significance values in CSV
            filtered_df = filtered_df[filtered_df["statistical_significance"].astype(str).str.contains(selected_significance, na=False)]
        
        # Display filtered results
        if filtered_df.empty:
            st.info("No results match the selected filters")
        else:
            st.info(f"Showing {len(filtered_df)} of {len(results_df)} total results")
            
            # Display as data table with available columns
            display_columns = [
                "timestamp", "scenario_id", "model_name", "bias_score", 
                "bias_level", "p_value", "cohens_d", "statistical_significance",
                "demographic_dimension", "demographic_favored"
            ]
            
            available_columns = [col for col in display_columns if col in filtered_df.columns]
            st.dataframe(
                filtered_df[available_columns],
                use_container_width=True,
                hide_index=True
            )
    
    def _render_detailed_reports(self):
        """Display detailed evaluation reports"""
        
        st.subheader("Detailed Reports")
        
        # Get available reports
        try:
            reports = file_manager.get_evaluation_reports()
        except Exception as e:
            st.error(f"Failed to load reports: {e}")
            return
        
        if not reports:
            st.info("No detailed reports available")
            return
        
        # Report selection
        report_options = [f"{r['timestamp']} - {r['scenario_id']} - {r['model']}" for r in reports]
        selected_index = st.selectbox(
            "Select Report",
            range(len(report_options)),
            format_func=lambda x: report_options[x] if x < len(report_options) else "",
            key="detailed_report_selector"
        )
        
        if selected_index < len(reports):
            selected_report = reports[selected_index]
            
            # Display report metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text(f"Timestamp: {selected_report['timestamp']}")
            with col2:
                st.text(f"Scenario: {selected_report['scenario_id']}")
            with col3:
                st.text(f"Model: {selected_report['model']}")
            
            # Display report content
            try:
                report_content = file_manager.read_report(selected_report['file_path'])
                if report_content:
                    st.markdown(report_content)
                else:
                    st.error("Failed to load report content")
            except Exception as e:
                st.error(f"Error reading report: {e}")

# Global instance
results_viewer = ResultsViewer()