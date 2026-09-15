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
            self._render_detailed_reports(results_df)
        
        return {"status": "displayed"}
    
    
    def _render_latest_results(self, results_df: pd.DataFrame):
        """Display the most recent evaluation results"""
        
        st.subheader("Latest Evaluations")
        
        # Sort by timestamp descending and get the 10 most recent results
        if 'timestamp' in results_df.columns:
            sorted_df = results_df.sort_values('timestamp', ascending=False)
        else:
            # Fallback: reverse the dataframe to get latest entries
            sorted_df = results_df.iloc[::-1]
        
        latest_results = sorted_df.head(10)
        
        if latest_results.empty:
            st.info("No recent results available")
            return
        
        # Display each result as an expandable card
        for idx, (_, row) in enumerate(latest_results.iterrows()):
            formatted_summary = data_formatter.format_results_summary(row)
            
            # Create expandable result card (framework prefix when the CSV carries it)
            framework = row.get("agentic_framework") if "agentic_framework" in row.index else None
            prefix = f"[{framework}] " if isinstance(framework, str) and framework else ""
            with st.expander(
                f"{prefix}{formatted_summary['Model']} - {formatted_summary['Scenario']} - {formatted_summary['Bias Level']} Bias",
                expanded=(idx == 0)  # Expand first result by default
            ):
                # Display key metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Bias Score", formatted_summary["Bias Score"])
                    st.metric("P-Value", formatted_summary["P-Value"])
                
                with col2:
                    st.metric("Effect Size", formatted_summary["Effect Size"])
                    st.metric("Bias Level", formatted_summary["Bias Level"])
                
                with col3:
                    st.metric("Statistical Significance", formatted_summary["Statistical Significance"])
                    if "Demographic Favored" in formatted_summary:
                        st.metric("Demographic Favored", formatted_summary["Demographic Favored"])
                
                # Additional details
                st.subheader("Detailed Information")
                for key, value in formatted_summary.items():
                    if key not in ["Bias Score", "P-Value", "Effect Size", "Bias Level", 
                                  "Statistical Significance", "Demographic Favored"]:
                        st.text(f"{key}: {value}")
    
    def _render_results_history(self, results_df: pd.DataFrame, key_prefix: str = "history"):
        """Display searchable/filterable results history"""
        
        st.subheader("Results History")
        
        # Filters - use actual values from CSV data
        col0, col1, col2, col3, col4 = st.columns(5)
        
        with col0:
            # Agent framework filter - only meaningful once the CSV carries the column
            has_framework_column = "agentic_framework" in results_df.columns
            if has_framework_column:
                framework_values = results_df["agentic_framework"].fillna("unknown").astype(str).unique().tolist()
                framework_options = ["All"] + sorted(framework_values)
            else:
                framework_options = ["All"]
            selected_framework = st.selectbox(
                "Framework", framework_options, key=f"{key_prefix}_framework_filter",
                disabled=not has_framework_column,
                help=None if has_framework_column else "agentic_framework column not present in research_results.csv"
            )
        
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
        
        if selected_framework != "All" and has_framework_column:
            filtered_df = filtered_df[filtered_df["agentic_framework"].fillna("unknown").astype(str) == selected_framework]
        
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
            
            # Sort by timestamp descending to show newest first
            if 'timestamp' in filtered_df.columns:
                filtered_df = filtered_df.sort_values('timestamp', ascending=False)
            
            # Display as data table with available columns
            display_columns = [
                "timestamp", "scenario_id", "model_name", "agentic_framework", "bias_score", 
                "bias_level", "p_value", "effect_size", "statistical_significance",
                "wilcoxon_reliable", "non_zero_differences",
                "demographic_dimension", "demographic_favored"
            ]
            
            available_columns = [col for col in display_columns if col in filtered_df.columns]
            st.dataframe(
                filtered_df[available_columns],
                width="stretch",
                hide_index=True
            )
    
    def _render_detailed_reports(self, results_df: pd.DataFrame = None):
        """Display detailed evaluation reports"""
        
        st.subheader("Detailed Reports")
        
        # Get available reports (joined to the CSV on evaluation_id for model/framework)
        try:
            reports = file_manager.get_evaluation_reports(results_df)
            
            if not reports:
                st.info("No detailed reports available")
                return
            
            # Re-sort reports by timestamp descending to ensure proper order
            from datetime import datetime
            def parse_timestamp(timestamp_str):
                try:
                    # Handle timestamp format: 2025-08-05_122134
                    if '_' in timestamp_str:
                        return datetime.strptime(timestamp_str, "%Y-%m-%d_%H%M%S")
                    # Handle date only format: 2025-08-05
                    elif len(timestamp_str.split('-')) >= 3:
                        return datetime.strptime(timestamp_str, "%Y-%m-%d")
                    # Handle year-month only: 2025-08
                    else:
                        return datetime.strptime(timestamp_str, "%Y-%m")
                except:
                    return datetime.min
            
            reports = sorted(reports, key=lambda x: parse_timestamp(x['timestamp']), reverse=True)
            
        except Exception as e:
            st.error(f"Failed to load reports: {e}")
            return
        
        if not reports:
            st.info("No detailed reports available")
            return
        
        st.caption(f"{len(reports)} reports, newest {reports[0]['timestamp']}")
        
        # Report selection - default to newest (index 0) since reports are sorted descending
        report_options = [
            f"{r['timestamp']} - {r['scenario_id']} - {r['model']}" + (f" [{r['framework']}]" if r.get('framework') else "")
            for r in reports
        ]
            
        selected_index = st.selectbox(
            "Select Report",
            range(len(report_options)),
            index=0,  # First item is newest after proper sorting
            format_func=lambda x: report_options[x] if x < len(report_options) else "",
            key="detailed_report_selector"
        )
        
        if selected_index < len(reports):
            selected_report = reports[selected_index]
            
            # Display report metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text(f"Timestamp: {selected_report['timestamp']}")
            with col2:
                st.text(f"Scenario: {selected_report['scenario_id']}")
            with col3:
                st.text(f"Model: {selected_report['model']}")
            with col4:
                st.text(f"Framework: {selected_report.get('framework') or 'n/a'}")
            
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