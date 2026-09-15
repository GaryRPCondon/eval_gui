"""
Headless smoke test of the Streamlit GUI using streamlit.testing.v1.AppTest.

No browser, no FastAPI, no agent run: the app is executed in-process and its
widgets inspected. Covers the framework selector, the scenario/framework
gating, the provider-list disk fallback, and the results page's framework
filter. Run on Windows from eval_gui/ with the LangGraph venv activated:

    ..\\agent_eval_langgraph\\Scripts\\activate && python -m pytest tests -v
"""

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

HERE = Path(__file__).resolve().parent
GUI_DIR = HERE.parent
sys.path.insert(0, str(GUI_DIR))


def _app() -> AppTest:
    at = AppTest.from_file(str(GUI_DIR / "app.py"), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    return at


def _labels(selectbox) -> list:
    # AppTest exposes selectbox options as formatted labels; value/set_value use the raw option value
    return list(selectbox.options)


def test_setup_page_renders_framework_selector():
    at = _app()
    fw = at.selectbox(key="framework_selector")
    assert fw.options[0] == "LangGraph" and fw.value == "langgraph"
    assert any(o.startswith("CAMEL-AI") for o in fw.options), fw.options
    # Scenario list comes from JSON titles with a kind suffix
    scen = at.selectbox(key="scenario_selector")
    labels = _labels(scen)
    assert labels and all("[single]" in l or "[multi]" in l for l in labels), labels
    # LLM list present (API or disk fallback)
    assert at.selectbox(key="llm_provider_selector").options


def test_start_button_enabled_for_available_framework():
    at = _app()
    assert any(b.label == "Start Evaluation" for b in at.button), [b.label for b in at.button]


def test_gpt5_disables_temperature_from_registry_flag():
    at = _app()
    llm = at.selectbox(key="llm_provider_selector")
    if "gpt5" not in llm.options:
        pytest.skip("gpt5 alias not configured")
    llm.set_value("gpt5").run()
    assert at.selectbox(key="temperature_selector").disabled is True
    llm.set_value("grok").run()
    assert at.selectbox(key="temperature_selector").disabled is False


def test_switching_to_camel_keeps_scenarios_runnable():
    at = _app()
    fw = at.selectbox(key="framework_selector")
    camel_label = next(o for o in fw.options if o.startswith("CAMEL-AI"))
    assert camel_label == "CAMEL-AI", f"CAMEL should be available in this checkout: {camel_label}"
    fw.set_value("camel").run()
    assert not at.exception, at.exception
    labels = _labels(at.selectbox(key="scenario_selector"))
    assert not any("no CAMEL-AI script" in l for l in labels), labels
    assert any(b.label == "Start Evaluation" for b in at.button)


def test_results_page_has_framework_filter():
    at = _app()
    at.button(key="nav_results").click().run()
    assert not at.exception, at.exception
    fw_filter = at.selectbox(key="results_framework_filter")
    assert fw_filter.options[0] == "All"
    if not fw_filter.disabled:
        assert "langgraph" in fw_filter.options


def test_monitor_page_shows_framework():
    at = _app()
    at.button(key="nav_monitor").click().run()
    assert not at.exception, at.exception
    texts = [t.value for t in at.text]
    assert any(v.startswith("Framework: LangGraph") for v in texts), texts


def test_detailed_reports_join_framework_from_csv():
    at = _app()
    at.button(key="nav_results").click().run()
    assert not at.exception, at.exception
    reports = at.selectbox(key="detailed_report_selector")
    assert reports.options, "no reports listed"
    # At least the CAMEL run recorded on 2026-09-15 should be tagged from the report header / CSV join
    assert any("[camel]" in o for o in reports.options), reports.options[:5]
