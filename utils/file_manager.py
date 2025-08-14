"""
File system utilities for reading scenarios, results, and reports
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import SCENARIOS_PATH, RESEARCH_RESULTS_CSV, REPORTS_PATH

class FileManager:
    
    @staticmethod
    def get_scenarios_list(scenario_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of scenario files from file system"""
        scenarios = []
        
        # Single agent scenarios
        if scenario_type is None or scenario_type == "single_agent":
            single_agent_path = SCENARIOS_PATH / "single_agent"
            if single_agent_path.exists():
                for scenario_file in single_agent_path.glob("*.json"):
                    try:
                        with open(scenario_file, 'r') as f:
                            data = json.load(f)
                            scenarios.append({
                                "id": scenario_file.stem,
                                "type": "single_agent",
                                "name": data.get("scenario_name", scenario_file.stem),
                                "description": data.get("scenario_description", "No description available"),
                                "file_path": str(scenario_file)
                            })
                    except Exception as e:
                        print(f"Error reading {scenario_file}: {e}")
        
        # Multi agent scenarios  
        if scenario_type is None or scenario_type == "multi_agent":
            multi_agent_path = SCENARIOS_PATH / "multi_agent"
            if multi_agent_path.exists():
                for scenario_file in multi_agent_path.glob("*.json"):
                    try:
                        with open(scenario_file, 'r') as f:
                            data = json.load(f)
                            scenarios.append({
                                "id": scenario_file.stem,
                                "type": "multi_agent", 
                                "name": data.get("scenario_name", scenario_file.stem),
                                "description": data.get("scenario_description", "No description available"),
                                "file_path": str(scenario_file)
                            })
                    except Exception as e:
                        print(f"Error reading {scenario_file}: {e}")
        
        return scenarios
    
    @staticmethod
    def read_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
        """Read specific scenario file"""
        # Try single agent first
        single_agent_file = SCENARIOS_PATH / "single_agent" / f"{scenario_id}.json"
        if single_agent_file.exists():
            try:
                with open(single_agent_file, 'r') as f:
                    data = json.load(f)
                    data["scenario_type"] = "single_agent"
                    return data
            except Exception as e:
                print(f"Error reading single agent scenario {scenario_id}: {e}")
        
        # Try multi agent
        multi_agent_file = SCENARIOS_PATH / "multi_agent" / f"{scenario_id}.json"
        if multi_agent_file.exists():
            try:
                with open(multi_agent_file, 'r') as f:
                    data = json.load(f)
                    data["scenario_type"] = "multi_agent"
                    return data
            except Exception as e:
                print(f"Error reading multi agent scenario {scenario_id}: {e}")
        
        return None
    
    @staticmethod
    def get_research_results() -> Optional[pd.DataFrame]:
        """Read research results CSV"""
        if RESEARCH_RESULTS_CSV.exists():
            try:
                return pd.read_csv(RESEARCH_RESULTS_CSV)
            except Exception as e:
                print(f"Error reading research results: {e}")
        return None
    
    @staticmethod
    def get_evaluation_reports() -> List[Dict[str, Any]]:
        """Get list of available evaluation reports"""
        reports = []
        if REPORTS_PATH.exists():
            for report_file in REPORTS_PATH.glob("*.md"):
                try:
                    # Parse filename for metadata
                    filename = report_file.stem
                    parts = filename.split('-')
                    
                    if len(parts) >= 3:
                        # Parse full timestamp: 2025-08-05_122134 format
                        timestamp_part = f"{parts[0]}-{parts[1]}-{parts[2]}"
                        # Handle cases where the timestamp includes time (YYYY-MM-DD_HHMMSS)
                        if '_' in timestamp_part:
                            timestamp = timestamp_part  # Keep full timestamp with time
                        else:
                            timestamp = f"{parts[0]}-{parts[1]}"  # Fallback for older format
                        
                        # Extract evaluation_id if present (new format: YYYY-MM-DD_HHMMSS-evaluation_id.md)
                        evaluation_id = ""
                        scenario_start_index = 3  # Default start for scenario parts
                        
                        if len(parts) == 3 and parts[1].startswith('mcp_eval_'):
                            # Current format: timestamp-evaluation_id-model.md
                            evaluation_id = parts[1]
                            scenario_start_index = 2  # Model part starts at index 2
                        elif len(parts) == 2 and parts[1].startswith('mcp_eval_'):
                            # Old simplified format: timestamp-evaluation_id.md
                            evaluation_id = parts[1]
                            scenario_start_index = len(parts)  # No more parts to process
                        elif len(parts) >= 4 and parts[1].startswith('mcp_eval_'):
                            # Old longer format: timestamp-evaluation_id-scenario-model.md
                            evaluation_id = parts[1]
                            scenario_start_index = 2
                        
                        scenario_parts = []
                        model_parts = []
                        
                        # Find where scenario ends and model begins
                        capturing_scenario = True
                        for part in parts[scenario_start_index:]:
                            if capturing_scenario and any(model_indicator in part.lower() 
                                                       for model_indicator in ['gpt', 'claude', 'deepseek', 'grok']):
                                capturing_scenario = False
                            
                            if capturing_scenario:
                                scenario_parts.append(part)
                            else:
                                model_parts.append(part)
                        
                        # Extract scenario and model info
                        if evaluation_id:
                            # Extract scenario from evaluation_id format: mcp_eval_scenario_xxxx
                            eval_parts = evaluation_id.split('_')
                            if len(eval_parts) >= 3:
                                scenario_id = '_'.join(eval_parts[2:-1])  # Skip mcp_eval and last number
                            else:
                                scenario_id = "unknown"
                            
                            # Extract model from filename parts if available
                            if scenario_start_index < len(parts):
                                model = '-'.join(parts[scenario_start_index:])
                            else:
                                model = "unknown"  # Old format without model in filename
                        else:
                            # Original format - extract from filename parts
                            scenario_id = '-'.join(scenario_parts) if scenario_parts else "unknown"
                            model = '-'.join(model_parts) if model_parts else "unknown"
                        
                        reports.append({
                            "filename": report_file.name,
                            "timestamp": timestamp,
                            "scenario_id": scenario_id,
                            "model": model,
                            "evaluation_id": evaluation_id,  # Add evaluation_id for linking
                            "file_path": str(report_file),
                            "size": report_file.stat().st_size
                        })
                except Exception as e:
                    print(f"Error parsing report filename {report_file}: {e}")
        
        # Sort by timestamp descending
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        return reports
    
    @staticmethod
    def read_report(report_path: str) -> Optional[str]:
        """Read specific evaluation report"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading report {report_path}: {e}")
            return None

# Global file manager instance  
file_manager = FileManager()