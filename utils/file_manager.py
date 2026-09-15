"""
File system utilities for reading scenarios, results, and reports
"""

import json
import re
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
                            presentation_data = data["presentation_data"]
                            scenarios.append({
                                "id": scenario_file.stem,
                                "type": "single_agent",
                                "name": presentation_data["title"],
                                "description": presentation_data["description"],
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
                            presentation_data = data["presentation_data"]
                            scenarios.append({
                                "id": scenario_file.stem,
                                "type": "multi_agent",
                                "name": presentation_data["title"],
                                "description": presentation_data["description"],
                                "file_path": str(scenario_file)
                            })
                    except Exception as e:
                        print(f"Error reading {scenario_file}: {e}")

        # Filter out placeholder scenarios if full research scenario exists
        scenarios = FileManager._filter_placeholders(scenarios)

        return scenarios

    @staticmethod
    def _filter_placeholders(scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove placeholder scenarios when equivalent full research scenario exists.
        Placeholder scenarios are named like 'placeholder_<scenario_name>' and have
        titles starting with '[PLACEHOLDER]'. If a full scenario exists without the
        'placeholder_' prefix, the placeholder version is hidden from the UI.
        """
        # Build set of all full scenario IDs (non-placeholder)
        full_scenario_ids = {
            s["id"] for s in scenarios
            if not s["id"].startswith("placeholder_")
        }

        # Filter out placeholders that have a corresponding full scenario
        filtered = []
        for scenario in scenarios:
            scenario_id = scenario["id"]

            # Check if this is a placeholder scenario
            if scenario_id.startswith("placeholder_"):
                # Get the full scenario ID by removing the placeholder_ prefix
                full_id = scenario_id.replace("placeholder_", "", 1)

                # Only include placeholder if full version doesn't exist
                if full_id not in full_scenario_ids:
                    filtered.append(scenario)
            else:
                # Always include non-placeholder scenarios
                filtered.append(scenario)

        return filtered
    
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
        """Read research results CSV with comprehensive error handling"""
        try:
            if not RESEARCH_RESULTS_CSV.exists():
                print(f"Research results CSV file not found: {RESEARCH_RESULTS_CSV}")
                print("This is normal if no evaluations have been run yet.")
                return None
            
            # Check if file is empty
            if RESEARCH_RESULTS_CSV.stat().st_size == 0:
                print(f"Research results CSV file is empty: {RESEARCH_RESULTS_CSV}")
                return None
            
            df = pd.read_csv(RESEARCH_RESULTS_CSV)
            
            # Check if DataFrame is effectively empty (only headers)
            if df.empty or len(df) == 0:
                print(f"Research results CSV contains no data rows: {RESEARCH_RESULTS_CSV}")
                return None
            
            return df
            
        except pd.errors.EmptyDataError:
            print(f"Research results CSV is empty or contains no data: {RESEARCH_RESULTS_CSV}")
            return None
        except pd.errors.ParserError as e:
            print(f"Error parsing research results CSV: {e}")
            return None
        except PermissionError:
            print(f"Permission denied accessing research results CSV: {RESEARCH_RESULTS_CSV}")
            return None
        except Exception as e:
            print(f"Unexpected error reading research results: {e}")
            return None
    
    # Report filenames: YYYY-MM-DD_HHMMSS-<evaluation_id>-<model>.md (see markdown_report_service._generate_filename)
    _REPORT_NAME_RE = re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2}_\d{6})-(?P<evaluation_id>mcp_eval_.+?_\d+)-(?P<model>.+)$")
    _REPORT_HEADER_MODEL_RE = re.compile(r"\*\*Model\*\*:\s*(.+?)\s*\|")
    _REPORT_HEADER_SCENARIO_RE = re.compile(r"\*\*Scenario\*\*:\s*(\S+)")
    _REPORT_HEADER_FRAMEWORK_RE = re.compile(r"\*\*Framework\*\*:\s*(\S+)")

    @staticmethod
    def _read_report_header(report_file: Path) -> Dict[str, str]:
        """Model, scenario and framework from the report's own header line (first few lines only)."""
        info: Dict[str, str] = {}
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                head = "".join([next(f, "") for _ in range(6)])
            for key, pattern in (("model", FileManager._REPORT_HEADER_MODEL_RE),
                                 ("scenario_id", FileManager._REPORT_HEADER_SCENARIO_RE),
                                 ("framework", FileManager._REPORT_HEADER_FRAMEWORK_RE)):
                match = pattern.search(head)
                if match:
                    info[key] = match.group(1).strip()
        except Exception as e:
            print(f"Error reading report header {report_file}: {e}")
        return info

    @staticmethod
    def get_evaluation_reports(results_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """List evaluation reports with metadata.

        Metadata comes, in order of preference, from the report header, from a
        join on evaluation_id against the research results CSV (when passed),
        and finally from the filename. Legacy filenames that match none of
        these fall back to "unknown".
        """
        by_evaluation_id: Dict[str, Dict[str, Any]] = {}
        if results_df is not None and "evaluation_id" in results_df.columns:
            for _, row in results_df.iterrows():
                by_evaluation_id[str(row["evaluation_id"])] = row

        reports = []
        if REPORTS_PATH.exists():
            for report_file in REPORTS_PATH.glob("*.md"):
                try:
                    match = FileManager._REPORT_NAME_RE.match(report_file.stem)
                    if match:
                        timestamp = match.group("timestamp")
                        evaluation_id = match.group("evaluation_id")
                        model = match.group("model")
                        # evaluation_id embeds the scenario: mcp_eval_<scenario_id>_<n>
                        scenario_id = evaluation_id[len("mcp_eval_"):].rsplit("_", 1)[0]
                    else:
                        parts = report_file.stem.split("-")
                        timestamp = "-".join(parts[:3]) if len(parts) >= 3 else report_file.stem
                        evaluation_id, model, scenario_id = "", "unknown", "unknown"

                    header = FileManager._read_report_header(report_file)
                    model = header.get("model", model)
                    scenario_id = header.get("scenario_id", scenario_id)
                    framework = header.get("framework")

                    csv_row = by_evaluation_id.get(evaluation_id)
                    if csv_row is not None:
                        if pd.notna(csv_row.get("model_name")):
                            model = str(csv_row.get("model_name"))
                        if framework is None and "agentic_framework" in csv_row.index and pd.notna(csv_row.get("agentic_framework")):
                            framework = str(csv_row.get("agentic_framework"))

                    reports.append({
                        "filename": report_file.name,
                        "timestamp": timestamp,
                        "scenario_id": scenario_id,
                        "model": model,
                        "framework": framework,
                        "evaluation_id": evaluation_id,
                        "file_path": str(report_file),
                        "size": report_file.stat().st_size
                    })
                except Exception as e:
                    print(f"Error parsing report {report_file}: {e}")
        
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