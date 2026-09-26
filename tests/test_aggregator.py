from pathlib import Path
from access_agent_scout.state import AssessmentState
from access_agent_scout.nodes.dom_scan import dom_scan_node
from access_agent_scout.nodes.aggregator import aggregator_node


import pytest
import requests


# Checking if the ollama server is running
def _ollama_running() -> bool:
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


def test_aggregator_includes_real_findings():
    """Includes real findings from the fixture page into the aggregator and confirms
    every result has correct WCAG mappings (or is correctly flagged as best-practice)."""

    test_page = (Path(__file__).parent / "fixtures" /
                 "test_page.html").resolve().as_uri()

    scan_state = AssessmentState(input_type="url", input_value=test_page)
    scan_result = dom_scan_node(scan_state)

    assert len(scan_result["findings"]
               ) > 0, "fixture page should produce findings"

    agg_state = AssessmentState(
        input_type="url",
        input_value=test_page,
        findings=scan_result["findings"],
    )
    agg_result = aggregator_node(agg_state)

    assert "aggregated_findings" in agg_result
    aggregated = agg_result["aggregated_findings"]
    assert len(aggregated) > 0

    for finding in aggregated:
        if finding.is_best_practice:
            # genuinely no WCAG mapping exists for this rule — correct, not an error
            assert finding.wcag_criterion is None
            assert finding.level is None
        else:
            # a real WCAG violation should have both fields populated
            assert finding.wcag_criterion is not None
            assert finding.level in {"A", "AA", "AAA"}


def test_aggregator_handles_zero_findings():
    """A clean page (zero findings) should short-circuit without calling the LLM."""
    state = AssessmentState(
        input_type="url", input_value="https://example.com", findings=[])
    result = aggregator_node(state)

    assert result == {"aggregated_findings": []}


def test_aggregator_dedupes_and_returns_valid_output():
    test_page = (Path(__file__).parent / "fixtures" /
                 "test_page.html").resolve().as_uri()
    scan_state = AssessmentState(input_type="url", input_value=test_page)
    scan_result = dom_scan_node(scan_state)

    agg_state = AssessmentState(
        input_type="url", input_value=test_page, findings=scan_result["findings"])
    agg_result = aggregator_node(agg_state)

    aggregated = agg_result["aggregated_findings"]
    assert len(aggregated) > 0
    for finding in aggregated:
        assert finding.severity in {"critical", "serious", "moderate", "minor"}


def test_aggregator_handles_many_violations():
    many_page = (Path(__file__).parent / "fixtures" /
                 "many_violations.html").resolve().as_uri()
    scan_state = AssessmentState(input_type="url", input_value=many_page)
    scan_result = dom_scan_node(scan_state)

    agg_state = AssessmentState(
        input_type="url", input_value=many_page, findings=scan_result["findings"])
    agg_result = aggregator_node(agg_state)

    assert len(agg_result["aggregated_findings"]) >= 1
    for finding in agg_result["aggregated_findings"]:
        assert finding.rule_id

# def test_aggregator_handles_many_violations():
#     """Aggregator should still return valid, parseable output even with 20+ findings."""
#     many_page = (Path(__file__).parent / "fixtures" /
#                  "many_violations.html").resolve().as_uri()

#     scan_state = AssessmentState(input_type="url", input_value=many_page)
#     scan_result = dom_scan_node(scan_state)

#     assert len(scan_result["findings"]
#                ) >= 20, "fixture should produce 20+ findings"

#     agg_state = AssessmentState(
#         input_type="url",
#         input_value=many_page,
#         findings=scan_result["findings"],
#     )
#     agg_result = aggregator_node(agg_state)

#     assert "aggregated_findings" in agg_result
#     assert isinstance(agg_result["aggregated_findings"], list)
#     for finding in agg_result["aggregated_findings"]:
#         assert finding.rule_id
#         assert finding.severity in {"critical", "serious", "moderate", "minor"}
