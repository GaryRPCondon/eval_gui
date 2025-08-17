"""
Data formatting utilities for display in Streamlit components
Pure display layer - reads values, does not contain business logic
"""

import json
import pandas as pd
from typing import Dict, Any

class DataFormatter:
    
    @staticmethod
    def format_scenario_for_display(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format scenario data for clean display"""
        # Extract data from the nested structure
        presentation_data = scenario_data.get("presentation_data", {})
        
        return {
            "Scenario Name": presentation_data.get("title", scenario_data.get("scenario_id", "Unknown")),
            "Description": presentation_data.get("description", "No description"),
            "Type": scenario_data.get("scenario_type", presentation_data.get("task_type", "unknown")),
            "Domain": presentation_data.get("domain", "unknown"),
            "Format": presentation_data.get("format", "unknown"),
            "Evaluation Method": presentation_data.get("evaluation_method", "unknown"),
            "Task Type": presentation_data.get("task_type", "unknown"),
            "Scenario ID": scenario_data.get("scenario_id", "unknown")
        }
    
    @staticmethod
    def format_json_for_tree_display(data: Dict[str, Any], max_depth: int = 3) -> str:
        """Format JSON data for tree-like display"""
        def _format_value(value, depth=0, max_depth=max_depth):
            indent = "  " * depth
            
            if depth >= max_depth and isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    return f"{indent}{{...{len(value)} items...}}"
                else:
                    return f"{indent}[...{len(value)} items...]"
            
            if isinstance(value, dict):
                if not value:
                    return f"{indent}{{}}"
                
                lines = [f"{indent}{{"]
                for k, v in value.items():
                    formatted_value = _format_value(v, depth + 1, max_depth)
                    if '\n' in formatted_value:
                        lines.append(f"{indent}  {k}:")
                        lines.append(formatted_value)
                    else:
                        lines.append(f"{indent}  {k}: {formatted_value.strip()}")
                lines.append(f"{indent}}}")
                return '\n'.join(lines)
            
            elif isinstance(value, list):
                if not value:
                    return f"{indent}[]"
                
                lines = [f"{indent}["]
                for i, item in enumerate(value):
                    formatted_item = _format_value(item, depth + 1, max_depth)
                    if '\n' in formatted_item:
                        lines.append(f"{indent}  {i}:")
                        lines.append(formatted_item)
                    else:
                        lines.append(f"{indent}  {i}: {formatted_item.strip()}")
                lines.append(f"{indent}]")
                return '\n'.join(lines)
            
            elif isinstance(value, str):
                return f'"{value}"'
            else:
                return str(value)
        
        return _format_value(data)
    
    @staticmethod
    def format_results_summary(results_row: pd.Series) -> Dict[str, Any]:
        """Format a results row for summary display - read all calculated values from CSV"""
        summary = {
            "Timestamp": results_row.get("timestamp", "Unknown"),
            "Scenario": results_row.get("scenario_id", "Unknown"),
            "Model": results_row.get("model_name", "Unknown"),
            "Temperature": results_row.get("temperature", "Unknown"),
            "Bias Score": f"{results_row.get('bias_score', 0):.1f}",
            "Bias Level": results_row.get("bias_level", "Unknown"),
            "P-Value": f"{results_row.get('p_value', 0):.4f}",
            "Effect Size": f"{results_row.get('effect_size', 0):.3f}",
            "Statistical Significance": results_row.get("statistical_significance", "Unknown"),
            "Wilcoxon Reliable": results_row.get("wilcoxon_reliable", "Unknown"),
            "Non-Zero Differences": results_row.get("non_zero_differences", 0),
            "Demographic Dimension": results_row.get("demographic_dimension", "Unknown"),
            "Demographic Favored": results_row.get("demographic_favored", "Unknown"),
            "Net Demographic Effect": f"{results_row.get('net_demographic_effect', 0):.1f}"
        }
        
        # Add demographic averages from CSV columns if available
        demographic_columns = [
            ("baseline_demoA_avg", "DemoA Baseline"),
            ("baseline_demoB_avg", "DemoB Baseline"), 
            ("variation_demoA_avg", "DemoA Variation"),
            ("variation_demoB_avg", "DemoB Variation")
        ]
        
        for csv_col, display_name in demographic_columns:
            if csv_col in results_row.index and pd.notna(results_row.get(csv_col)):
                summary[display_name] = f"{results_row.get(csv_col, 0):.1f}"
        
        # Add amplification data for multi-agent scenarios
        if results_row.get("scenario_type") == "multi_agent":
            summary["Amplification Factor"] = f"{results_row.get('amplification_factor', 0):.1f}"
            stage_progression = results_row.get('stage_progression', '')
            if stage_progression and stage_progression != '':
                summary["Stage Progression"] = stage_progression
        
        return summary

# Global data formatter instance
data_formatter = DataFormatter()