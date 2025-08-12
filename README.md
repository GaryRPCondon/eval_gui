# AI Agent Evaluation Platform - GUI

A Streamlit-based web interface for the AI Agent Evaluation Platform, enabling researchers to configure, execute, and analyze bias evaluations across different AI models and scenarios.

## Features

- **Scenario Management**: Browse and select evaluation scenarios with detailed JSON viewing
- **Model Configuration**: Dynamic selection of available LLM providers with temperature control
- **Real-time Execution**: Run evaluations with live progress monitoring and console output
- **Results Analysis**: View evaluation results, statistical analysis, and detailed reports
- **History Management**: Browse and filter historical evaluation results

## Quick Start

### Launch All Services
Use the provided batch script to start all services:
```batch
start_services.bat
```

This launches:
- FastAPI Server (localhost:8000)
- MCP Server 
- GUI Server (localhost:8501)

### Access GUI
Open browser to `http://localhost:8501`

## Prerequisites

1. **Virtual Environment**: `agent_eval_langgraph` must be set up
2. **Windows Command Line**: Must run from Windows (not WSL)
3. **API Keys**: LLM provider keys configured in environment

## Architecture

### Pure Display Layer
- GUI contains **no business logic**
- All calculations performed by evaluation service
- Results read from CSV files and markdown reports
- Configuration read from existing config files

### Component Structure
```
eval_gui/
├── app.py                    # Main Streamlit application
├── components/
│   ├── scenario_browser.py   # Scenario selection and viewing
│   ├── llm_selector.py       # LLM configuration
│   ├── execution_monitor.py  # Progress tracking and logs
│   └── results_viewer.py     # Results display and reports
├── utils/
│   ├── api_client.py         # API calls to eval service
│   ├── file_manager.py       # File system operations
│   └── data_formatter.py     # Data display formatting
└── config/
    └── settings.py           # GUI configuration
```

### Integration Patterns
- **Scenarios**: Direct file system access to `scenarios/`
- **LLM Providers**: API call to evaluation service
- **Execution**: Subprocess calls to agent scripts
- **Results**: Direct file system access to `results/`

## Usage Workflow

1. **Setup Tab**: Select scenario and model configuration
2. **Execute Tab**: Run evaluation with real-time monitoring
3. **Results Tab**: View latest results and analysis
4. **History Tab**: Browse and filter historical results

## Troubleshooting

**"Evaluation service: Disconnected"**
- Ensure all services launched via batch script
- Check FastAPI service is running on port 8000

**"No scenarios found"**
- Verify file paths in `config/settings.py`
- Check scenarios directory exists and contains JSON files

**"Execution failed"**
- Ensure running from Windows environment (not WSL)
- Verify virtual environment is activated
- Check API keys are configured

**"No results found"**
- Run an evaluation to generate results
- Check results directory contains CSV files

## Development Notes

### Design Principles
- Pure display layer - no business logic duplication
- Read calculated values from CSV/markdown - no recalculation
- Configuration-driven - read from existing config files
- Framework agnostic - works with any agent implementation

### Adding Features
- New metrics: Update CSV schema, no GUI changes needed
- New filters: Read unique values from CSV data
- New views: Add components following existing patterns