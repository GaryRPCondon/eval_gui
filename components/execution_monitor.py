"""
Execution monitoring component for running evaluations and tracking progress
"""

import streamlit as st
import subprocess
import threading
import time
import os
from typing import Dict, Any, Optional
from config.settings import LANGGRAPH_AGENT_PATH, PROJECT_ROOT

class ExecutionMonitor:
    
    def __init__(self):
        self.process = None
        self.output_lines = []
        self.is_running = False
        
    def render(self, scenario_config: Dict[str, Any], llm_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render execution interface"""
        
        st.header("Evaluation Execution")
        
        # Check if we have required configuration
        if not scenario_config.get("selected_scenario") or not llm_config.get("selected_provider"):
            st.warning("Please select both a scenario and LLM provider before running evaluation")
            return {"status": "not_configured"}
        
        scenario = scenario_config["selected_scenario"]
        provider = llm_config["selected_provider"]
        temperature = llm_config["temperature"]
        verbose = llm_config["verbose"]
        
        # Display execution summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Execution Configuration")
            st.text(f"Scenario: {scenario['name']} ({scenario['type']})")
            st.text(f"Model: {provider}")
            st.text(f"Temperature: {temperature}")
            st.text(f"Verbose Mode: {'Enabled' if verbose else 'Disabled'}")
        
        with col2:
            # Execution controls
            if not self.is_running:
                if st.button("Start Evaluation", type="primary", key="start_eval_button"):
                    return self._start_evaluation(scenario, provider, temperature, verbose)
            else:
                if st.button("Cancel Evaluation", type="secondary", key="cancel_eval_button"):
                    return self._cancel_evaluation()
                
                # Show running status
                st.info("Evaluation running...")
        
        # Progress and status section
        if self.is_running or self.output_lines:
            self._render_execution_status()
        
        return {"status": "ready"}
    
    def _start_evaluation(self, scenario: Dict[str, Any], provider: str, temperature: float, verbose: bool) -> Dict[str, Any]:
        """Start evaluation execution"""
        
        try:
            # Determine the correct script based on scenario type and ID
            script_name = self._get_agent_script(scenario)
            
            # Build Windows command with virtual environment activation
            # Based on CLAUDE.md: Must be run from Windows command line with agent_eval_langgraph virtual environment
            venv_activation = r"..\agent_eval_langgraph\Scripts\activate"
            
            # Build python command with all arguments
            # Running from langgraph_agent directory, so script is in current directory
            python_args = [script_name, provider]
            
            # Add temperature if not default
            if temperature != 0.1:
                python_args.extend(["-t", str(temperature)])
            
            # Add verbose flag
            if verbose:
                python_args.append("-v")
            
            python_command = f"python {' '.join(python_args)}"
            command = ["cmd.exe", "/c", f"{venv_activation} && {python_command}"]
            
            # Start process
            self.output_lines = []
            self.is_running = True
            
            # Use subprocess.Popen for real-time output capture
            # Working directory must be langgraph_agent for relative paths to work
            self.process = subprocess.Popen(
                command,
                cwd=str(LANGGRAPH_AGENT_PATH),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Start output monitoring thread
            threading.Thread(target=self._monitor_output, daemon=True).start()
            
            st.success(f"Started evaluation: {' '.join(command)}")
            return {"status": "started"}
            
        except Exception as e:
            st.error(f"Failed to start evaluation: {e}")
            self.is_running = False
            return {"status": "error", "error": str(e)}
    
    def _cancel_evaluation(self) -> Dict[str, Any]:
        """Cancel running evaluation"""
        
        try:
            if self.process:
                self.process.terminate()
                self.process = None
            
            self.is_running = False
            st.warning("Evaluation cancelled")
            return {"status": "cancelled"}
            
        except Exception as e:
            st.error(f"Failed to cancel evaluation: {e}")
            return {"status": "error", "error": str(e)}
    
    def _monitor_output(self):
        """Monitor subprocess output in background thread"""
        
        try:
            if not self.process:
                return
            
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_lines.append(line.strip())
            
            # Wait for process to complete
            self.process.wait()
            self.is_running = False
            
            # Add completion message
            if self.process.returncode == 0:
                self.output_lines.append("=== EVALUATION COMPLETED SUCCESSFULLY ===")
            else:
                self.output_lines.append(f"=== EVALUATION FAILED (exit code: {self.process.returncode}) ===")
                
        except Exception as e:
            self.output_lines.append(f"=== OUTPUT MONITORING ERROR: {e} ===")
            self.is_running = False
    
    def _render_execution_status(self):
        """Render execution progress and console output"""
        
        # Status indicator
        if self.is_running:
            st.info("Evaluation in progress...")
        elif self.output_lines and "COMPLETED SUCCESSFULLY" in self.output_lines[-1]:
            st.success("Evaluation completed successfully")
        elif self.output_lines and "FAILED" in self.output_lines[-1]:
            st.error("Evaluation failed")
        
        # Console output
        if self.output_lines:
            with st.expander("Console Output", expanded=True):
                # Show last 50 lines to avoid overwhelming the interface
                recent_lines = self.output_lines[-50:] if len(self.output_lines) > 50 else self.output_lines
                output_text = "\n".join(recent_lines)
                st.code(output_text, language="text")
                
                # Auto-scroll indicator
                if self.is_running and len(self.output_lines) > 50:
                    st.caption(f"Showing last 50 lines of {len(self.output_lines)} total lines")
    
    def _get_agent_script(self, scenario: Dict[str, Any]) -> str:
        """Get the appropriate agent script for a scenario"""
        scenario_id = scenario["id"]
        scenario_type = scenario["type"]
        
        # Use a simple mapping based on scenario characteristics
        if scenario_type == "single_agent":
            return "agent.py"
        elif "parole_board" in scenario_id:
            if "control" in scenario_id:
                return "control_parole_board_agent.py"
            else:
                return "parole_board_agent.py"
        elif "medical" in scenario_id and "multi_agent" in scenario_type:
            return "medical_resume_evaluator.py"
        else:
            # Default fallback
            return "parole_board_agent.py"

# Global instance
execution_monitor = ExecutionMonitor()