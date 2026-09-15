# AI Agent Evaluation Platform - GUI

A Streamlit web interface for the AI Agent Evaluation Platform: pick an agent
framework, a scenario and a model, run the evaluation with live console output,
and browse the results the evaluation service produced.

## Features

- **Framework Selection**: run the same scenario with any registered agent framework (LangGraph, CAMEL-AI)
- **Scenario Management**: browse and select evaluation scenarios with detailed JSON viewing
- **Model Configuration**: dynamic selection of LLM providers with temperature control
- **Real-time Execution**: run evaluations with live progress monitoring and console output
- **Results Analysis**: view evaluation results, statistical analysis and detailed reports, filterable by framework
- **History Management**: browse and filter historical evaluation results

## Quick Start (Windows)

```bat
cd C:\Work\Masters\Thesis\Implementation
agent_eval_langgraph\Scripts\activate
cd eval_gui
streamlit run app.py
```

Open `http://localhost:8501`.

The GUI itself runs in the LangGraph venv (it needs Streamlit and pandas). Each
agent framework runs in its own venv, which the GUI activates when it launches
an evaluation. The evaluation service's FastAPI server (`localhost:8000`) is
optional: it is used for the provider list, and when it is down the GUI reads
the same list from `agent_eval_service/config/llm_providers.py` and says so in
a caption. Agent runs do not need FastAPI; each agent starts its own MCP
server.

## Prerequisites

1. **Windows**: agent launches activate a Windows venv through `cmd.exe`
2. **One venv per framework**, as siblings of the agent folders under the Implementation root:

   | Framework | Agent folder | Virtual environment |
   |---|---|---|
   | LangGraph | `langgraph_agent/` | `agent_eval_langgraph/` |
   | CAMEL-AI | `camel_agent/` | `agent_eval_camel/` |

   A framework whose folder or venv is missing is still listed, marked
   "(unavailable)" with the reason, and cannot be started.
3. **API keys** in `agent_eval_service/.env`

## Frameworks

The list of frameworks, their folders and venvs lives in one place:
`agent_eval_service/config/agent_frameworks.py`. The GUI loads it off disk,
exactly as it loads `llm_providers.py`, and never hard-codes a framework.

Run `python agent_eval_service\config\agent_frameworks.py` for an availability
report.

### Adding a framework

1. Add an entry to `AGENT_FRAMEWORKS` in `agent_frameworks.py` (display name, agent folder, venv folder).
2. Create the agent folder and venv as siblings of the existing ones.
3. Name each agent script after its scenario id (`parole_board_multiAgent.py` and so on) and give it the standard CLI: `<model>` positional, `-t/--temperature`, `-v/--verbose`, `--n/--max-candidates`.
4. Have the agent pass its framework id as `agentic_framework` when it submits results, so the CSV and reports carry it.

No GUI change is needed. Because the two service config modules are cached
per Streamlit server process, use "Clear cache" from the app menu (or restart)
after editing them.

## Architecture

### Pure Display Layer
- GUI contains **no business logic**
- All calculations performed by the evaluation service
- Results read from CSV files and markdown reports
- Configuration read from existing service config files

### Component Structure
```
eval_gui/
├── app.py                        # Main Streamlit application (Setup / Monitor / Results)
├── components/
│   ├── framework_selector.py     # Agent framework selection (from the registry)
│   ├── scenario_browser.py       # Scenario selection and viewing
│   ├── llm_selector.py           # LLM configuration
│   ├── execution_monitor.py      # Launch, progress tracking and console
│   └── results_viewer.py         # Results display and reports
├── utils/
│   ├── service_config.py         # Off-disk loader for llm_providers.py / agent_frameworks.py
│   ├── api_client.py             # Provider list from the eval service API (optional)
│   ├── file_manager.py           # File system operations
│   └── data_formatter.py         # Data display formatting
├── config/
│   └── settings.py               # GUI configuration
└── tests/
    └── test_app_smoke.py         # Headless Streamlit AppTest suite
```

### Integration Patterns
- **Frameworks**: `agent_frameworks.py` registry, loaded off disk
- **Scenarios**: direct file system access to `agent_eval_service/scenarios/`
- **LLM Providers**: evaluation service API, falling back to `llm_providers.py`
- **Execution**: subprocess launch of `<agent folder>\<scenario_id>.py` inside that framework's venv; completion and failure are read from the process exit code; Cancel kills the whole process tree (agent and its MCP server)
- **Results**: direct file system access to `agent_eval_service/results/`; the `agentic_framework` column drives the Framework filter and column, and reports are joined to CSV rows by evaluation id

## Usage Workflow

1. **Setup**: choose framework, scenario and model configuration, then Start Evaluation
2. **Monitor**: live console output; the run can be cancelled
3. **Results**: latest results, filterable history, detailed reports

## Testing

Headless, no browser, no FastAPI, no agent run:

```bat
cd eval_gui
..\agent_eval_langgraph\Scripts\activate
python -m pytest tests -v
```

Uses `streamlit.testing.v1.AppTest` to execute the app in-process and inspect
its widgets: framework selector defaults and availability, scenario labels and
gating, temperature disabling from the provider flag, the results page's
framework filter, the Monitor page summary, and the report/CSV join. The
registry itself is covered by `tests/unit/test_agent_frameworks.py` at the
Implementation root.

## Troubleshooting

**"Evaluation service API unreachable; provider list loaded from llm_providers.py"**
- Informational. Start FastAPI on port 8000 if you want the API path.

**A framework shows "(unavailable)"**
- The caption gives the reason: the agent folder or its venv is missing. Check the table under Prerequisites.

**"... has no script named <scenario>.py"**
- The selected framework does not implement that scenario yet. Pick another scenario or framework.

**"Agent launch is supported from Windows only"**
- Run the GUI from Windows, not WSL.

**"No scenarios found"**
- Check `agent_eval_service/scenarios/` contains JSON files.

**"No results found"**
- Run an evaluation to generate results.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite it as:

```bibtex
@software{Condon_AI_Agent_Evaluation_GUI_2026,
  author = {Condon, Gary},
  title = {AI Agent Evaluation GUI},
  year = {2026},
  url = {https://github.com/GaryRPCondon/eval_gui},
  version = {1.1.0}
}
```

Or cite the related thesis:

```bibtex
@mastersthesis{Condon_Bias_Evaluation_Framework_2025,
  author = {Condon, Gary},
  title = {Towards a framework for Bias Evaluation of AI Agents in Agentic Workflows},
  school = {Technological University Dublin},
  year = {2025},
  type = {Master's Thesis}
}
```

For citation in other formats, see [CITATION.cff](CITATION.cff).

## Related Repositories

- **[agent_eval_service](https://github.com/GaryRPCondon/agent_eval_service)**: core evaluation service with bias detection and statistical analysis; owns the framework registry
- **[langgraph_agent](https://github.com/GaryRPCondon/langgraph_agent)**: LangGraph evaluation agents
- **[camel_agent](https://github.com/GaryRPCondon/camel_agent)**: CAMEL-AI evaluation agents

## Support

For questions, issues, or collaboration opportunities:
- Open an issue on GitHub
- Contact: garyrcondon@gmail.com
