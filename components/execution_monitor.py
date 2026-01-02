"""
Execution monitoring component for running evaluations and tracking progress
Improved version with fixed-height scrollable console
"""

import streamlit as st
import subprocess
import threading
import time
import os
from typing import Dict, Any, Optional, List
from config.settings import LANGGRAPH_AGENT_PATH, PROJECT_ROOT

class ExecutionMonitor:
    
    def __init__(self):
        pass

    def _init_state(self):
        """Initialize session state for this component if not exists"""
        if 'monitor_process' not in st.session_state:
            st.session_state.monitor_process = None
            st.session_state.monitor_output = []
            st.session_state.monitor_is_running = False
        
    @property
    def process(self):
        return st.session_state.monitor_process
    
    @process.setter
    def process(self, value):
        st.session_state.monitor_process = value
        
    @property
    def output_lines(self):
        return st.session_state.monitor_output
        
    @property
    def is_running(self):
        return st.session_state.monitor_is_running
    
    @is_running.setter
    def is_running(self, value):
        st.session_state.monitor_is_running = value
        
    def render(self, scenario_config: Dict[str, Any], llm_config: Dict[str, Any], hide_config: bool = False) -> Dict[str, Any]:
        """Render execution interface"""
        self._init_state()
        
        # Check if we have required configuration
        if not scenario_config.get("selected_scenario") or not llm_config.get("selected_provider"):
            st.warning("Please configure scenario and LLM provider in the Setup tab first")
            return {"status": "not_configured"}
        
        scenario = scenario_config["selected_scenario"]
        provider = llm_config["selected_provider"]
        temperature = llm_config["temperature"]
        verbose = llm_config["verbose"]
        
        # Auto-start if requested from setup tab (only once)
        if st.session_state.get('start_execution', False):
            st.session_state.start_execution = False  # Clear flag immediately
            
            if not self.is_running:
                # Auto-start the evaluation silently
                self._start_evaluation(scenario, provider, temperature, verbose)
                st.rerun() # Rerun to pick up the running state
            else:
                st.warning("Evaluation is already running!")
        
        # Show configuration only if not hidden
        if not hide_config:
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
                        self._start_evaluation(scenario, provider, temperature, verbose)
                        st.rerun()
                else:
                    if st.button("Cancel Evaluation", type="secondary", key="cancel_eval_button"):
                        self._cancel_evaluation()
                        st.rerun()
        else:
            # Simplified hidden interface - just cancel option if running
            if self.is_running:
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("Cancel", type="secondary", key="cancel_eval_button"):
                        self._cancel_evaluation()
                        st.rerun()
        
        # Render the monitoring area with auto-refresh
        self._render_monitor_area()
        
        return {"status": "running" if self.is_running else "ready"}

    @st.fragment(run_every=1)
    def _render_monitor_area(self):
        """
        Render the monitoring area. 
        This fragment automatically refreshes every 1 second.
        """
        # Check process status and update state if needed
        if self.is_running and self.process:
            if self.process.poll() is not None:
                self.is_running = False
                # Force a rerun to update the UI immediately after completion
                st.rerun()

        # Status display
        if self.is_running:
            st.info(f"🔄 Evaluation running...")
        elif self.output_lines:
            if any("COMPLETED SUCCESSFULLY" in line for line in self.output_lines):
                st.success("✅ Evaluation completed successfully!")
            elif any("FAILED" in line for line in self.output_lines):
                st.error("❌ Evaluation failed")
            else:
                st.info("⏸️ Evaluation stopped")
        else:
            st.info(f"Ready to start.")


        # Console output
        if self.output_lines:
            # Display line count
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("Console Output")
            with col2:
                st.caption(f"{len(self.output_lines)} lines")
            
            # Escape HTML to prevent any interpretation
            import html
            output_text = html.escape("\n".join(self.output_lines))
            
            # Use components.html to render the console properly
            import streamlit.components.v1 as components
            
            console_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background-color: #0e1117;
                    }}
                    #console-output {{
                        height: 500px;
                        overflow-y: scroll;
                        overflow-x: auto;
                        background-color: #0e1117;
                        border: 1px solid #262730;
                        border-radius: 0.5rem;
                        scrollbar-width: thin;
                        scrollbar-color: #888 #2b2b2b;
                    }}
                    #console-output::-webkit-scrollbar {{
                        width: 14px;
                        height: 14px;
                    }}
                    #console-output::-webkit-scrollbar-track {{
                        background: #2b2b2b;
                    }}
                    #console-output::-webkit-scrollbar-thumb {{
                        background-color: #888;
                        border-radius: 7px;
                        border: 3px solid #2b2b2b;
                    }}
                    #console-output::-webkit-scrollbar-thumb:hover {{
                        background-color: #aaa;
                    }}
                    pre {{
                        margin: 0;
                        padding: 1rem;
                        color: #fafafa;
                        font-family: 'Courier New', monospace;
                        font-size: 15px;
                        line-height: 1.4;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }}
                </style>
            </head>
            <body>
                <div id="console-output">
                    <pre>{output_text}</pre>
                </div>
                <script>
                    (function() {{
                        var consoleDiv = document.getElementById("console-output");
                        if (consoleDiv) {{
                            function scrollToBottom() {{
                                consoleDiv.scrollTop = consoleDiv.scrollHeight;
                            }}
                            scrollToBottom();
                            setTimeout(scrollToBottom, 10);
                            setTimeout(scrollToBottom, 50);
                            setTimeout(scrollToBottom, 150);
                            setTimeout(scrollToBottom, 300);
                        }}
                    }})();
                </script>
            </body>
            </html>
            """
            
            components.html(console_html, height=520, scrolling=False)




    def _start_evaluation(self, scenario: Dict[str, Any], provider: str, temperature: float, verbose: bool):
        """Start evaluation execution"""
        
        try:
            # Determine the correct script based on scenario type and ID
            script_name = self._get_agent_script(scenario)
            
            # Build Windows command with virtual environment activation
            venv_activation = r"..\agent_eval_langgraph\Scripts\activate"
            
            # Build python command with all arguments
            python_args = [script_name, provider]
            
            # Check if provider supports temperature before adding the argument
            try:
                import importlib.util
                llm_providers_path = LANGGRAPH_AGENT_PATH.parent / "agent_eval_service" / "config" / "llm_providers.py"
                spec = importlib.util.spec_from_file_location("llm_providers", llm_providers_path)
                llm_providers_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(llm_providers_module)
                
                provider_config = llm_providers_module.get_provider_config(provider)
                provider_supports_temp = provider_config.get("supports_temperature", True)
                
                if temperature != 0.1 and provider_supports_temp:
                    python_args.extend(["-t", str(temperature)])
                elif temperature != 0.1 and not provider_supports_temp:
                    if verbose:
                        print(f"Warning: {provider} does not support temperature parameter. Using model default.")
                        
            except Exception as e:
                if temperature != 0.1:
                    python_args.extend(["-t", str(temperature)])
            
            if verbose:
                python_args.append("-v")
            
            python_command = f"python {' '.join(python_args)}"
            command = ["cmd.exe", "/c", f"{venv_activation} && {python_command}"]
            
            # Reset state
            self.output_lines.clear()
            self.output_lines.append(f"Starting command: {' '.join(command)}")
            self.is_running = True
            
            # Start process
            process = subprocess.Popen(
                command,
                cwd=str(LANGGRAPH_AGENT_PATH),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.process = process
            
            # Start output monitoring thread
            # Pass the list and process explicitly to avoid session_state access in thread
            threading.Thread(
                target=self._monitor_output, 
                args=(self.output_lines, process),
                daemon=True
            ).start()
            
        except Exception as e:
            st.error(f"Failed to start evaluation: {e}")
            self.is_running = False
    
    def _cancel_evaluation(self):
        """Cancel running evaluation"""
        try:
            if self.process:
                self.process.terminate()
                self.process = None
            
            self.is_running = False
            self.output_lines.append("=== EVALUATION CANCELLED BY USER ===")
            
        except Exception as e:
            st.error(f"Failed to cancel evaluation: {e}")
    
    def _monitor_output(self, output_list: List[str], process: subprocess.Popen):
        """
        Monitor subprocess output in background thread.
        Uses explicit arguments instead of session_state to be thread-safe.
        """
        try:
            if not process:
                return
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    output_list.append(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                output_list.append("=== EVALUATION COMPLETED SUCCESSFULLY ===")
            else:
                output_list.append(f"=== EVALUATION FAILED (exit code: {process.returncode}) ===")
        
        except Exception as e:
            output_list.append(f"=== OUTPUT MONITORING ERROR: {e} ===")

    def _get_agent_script(self, scenario: Dict[str, Any]) -> str:
        """Get the appropriate agent script for a scenario"""
        scenario_id = scenario["id"]
        
        if scenario_id == "medical_hiring_singleAgent":
            return "medical_hiring_singleAgent.py"
        elif scenario_id == "medical_hiring_multiAgent":
            return "medical_hiring_multiAgent.py"
        elif scenario_id == "parole_board_multiAgent":
            return "parole_board_multiAgent.py"
        elif scenario_id == "controlTest_parole_board_multiAgent":
            return "controlTest_parole_board_multiAgent.py"
        else:
            raise ValueError(f"Unknown scenario_id: {scenario_id}")

# Global instance
execution_monitor = ExecutionMonitor()
