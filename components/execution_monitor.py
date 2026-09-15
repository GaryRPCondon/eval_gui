"""
Execution monitoring component for running evaluations and tracking progress
Improved version with fixed-height scrollable console
"""

import html
import os
import subprocess
import threading
from typing import Dict, Any, List

import streamlit as st
import streamlit.components.v1 as components

from config.settings import PROJECT_ROOT
from utils import service_config

class ExecutionMonitor:
    
    def __init__(self):
        pass

    def _init_state(self):
        """Initialize session state for this component if not exists"""
        if 'monitor_process' not in st.session_state:
            st.session_state.monitor_process = None
            st.session_state.monitor_output = []
            st.session_state.monitor_is_running = False
            st.session_state.monitor_returncode = None
            st.session_state.monitor_cancelled = False
        
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
    
    @property
    def returncode(self):
        return st.session_state.monitor_returncode
    
    @returncode.setter
    def returncode(self, value):
        st.session_state.monitor_returncode = value
    
    @property
    def cancelled(self):
        return st.session_state.monitor_cancelled
    
    @cancelled.setter
    def cancelled(self, value):
        st.session_state.monitor_cancelled = value
        
    def render(self, scenario_config: Dict[str, Any], llm_config: Dict[str, Any], framework_config: Dict[str, Any] = None, hide_config: bool = False) -> Dict[str, Any]:
        """Render execution interface"""
        self._init_state()
        framework_config = framework_config or {}
        
        # Check if we have required configuration
        if not scenario_config.get("selected_scenario") or not llm_config.get("selected_provider") or not framework_config.get("selected_framework"):
            st.warning("Please configure framework, scenario and LLM provider in the Setup tab first")
            return {"status": "not_configured"}
        
        framework_id = framework_config["selected_framework"]
        framework_name = framework_config.get("display_name", framework_id)
        scenario = scenario_config["selected_scenario"]
        provider = llm_config["selected_provider"]
        temperature = llm_config["temperature"]
        verbose = llm_config["verbose"]
        
        # Auto-start if requested from setup tab (only once)
        if st.session_state.get('start_execution', False):
            st.session_state.start_execution = False  # Clear flag immediately
            
            if not self.is_running:
                # Auto-start the evaluation silently
                self._start_evaluation(framework_id, scenario, provider, temperature, verbose)
                st.rerun() # Rerun to pick up the running state
            else:
                st.warning("Evaluation is already running!")
        
        # Show configuration only if not hidden
        if not hide_config:
            # Display execution summary
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Execution Configuration")
                st.text(f"Framework: {framework_name}")
                st.text(f"Scenario: {scenario['name']} ({scenario['type']})")
                st.text(f"Model: {provider}")
                st.text(f"Temperature: {temperature}")
                st.text(f"Verbose Mode: {'Enabled' if verbose else 'Disabled'}")
            
            with col2:
                # Execution controls
                if not self.is_running:
                    if st.button("Start Evaluation", type="primary", key="start_eval_button"):
                        self._start_evaluation(framework_id, scenario, provider, temperature, verbose)
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
            code = self.process.poll()
            if code is not None:
                self.returncode = code
                self.is_running = False
                # Force a rerun to update the UI immediately after completion
                st.rerun()

        # Status display, driven by the exit code rather than by matching words in the console output
        if self.is_running:
            st.info(f"🔄 Evaluation running...")
        elif self.cancelled:
            st.info("⏸️ Evaluation stopped by user")
        elif self.returncode == 0:
            st.success("✅ Evaluation completed successfully!")
        elif self.returncode is not None:
            st.error(f"❌ Evaluation failed (exit code {self.returncode})")
        elif self.output_lines:
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
            output_text = html.escape("\n".join(self.output_lines))
            
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




    def _start_evaluation(self, framework_id: str, scenario: Dict[str, Any], provider: str, temperature: float, verbose: bool):
        """Start evaluation execution via the framework registry"""
        
        if os.name != 'nt':
            st.error("Agent launch is supported from Windows only (the agents activate a Windows venv via cmd.exe).")
            return
        
        try:
            # Temperature is passed whenever the provider supports it, so the script runs the value shown in the GUI
            supports_temp = service_config.provider_supports_temperature(provider)
            launch = service_config.agent_frameworks().build_launch_command(
                framework_id,
                scenario["id"],
                provider,
                temperature=temperature if supports_temp else None,
                verbose=verbose,
                project_root=PROJECT_ROOT,
            )
            command = launch["command"]
            
            # Reset state
            self.output_lines.clear()
            self.output_lines.append(f"[{framework_id}] cwd: {launch['cwd']}")
            self.output_lines.append(f"Starting command: {launch['shell']}")
            if not supports_temp:
                self.output_lines.append(f"Note: {provider} does not support the temperature parameter; model default will be used.")
            self.returncode = None
            self.cancelled = False
            self.is_running = True
            
            # Start process
            process = subprocess.Popen(
                command,
                cwd=str(launch["cwd"]),
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
        """Cancel running evaluation, taking the whole process tree (cmd.exe, python agent, its MCP server)"""
        try:
            if self.process:
                if os.name == 'nt':
                    subprocess.run(
                        ["taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except Exception:
                    pass
                self.process = None
            
            self.cancelled = True
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

# Global instance
execution_monitor = ExecutionMonitor()
