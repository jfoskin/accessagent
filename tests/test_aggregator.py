from pathlib import Path
from access_agent_scout.state import AssessmentState
from access_agent_scout.nodes.dom_scan import dom_scan_node
from access_agent_scout.nodes.aggregator import aggregator_node


def test_aggregator_includes_real_findings():
    """Includes real findings from the fixture page into the aggregator and confirms every result has real WCAG mappings """

    test_page = (Path(__file__).parent/"fixtures" /
                 "test_page.html").resolve().as_uri()

    scan_state = AssessmentState(input_type="url", input_value=test_page)
    scan_result = dom_scan_node(scan_state)

    assert len(scan_result["findings"]
               ) > 0, "fixture page should produce findings"

    # add the real findings into a fresh state for the aggregator
    agg_state = AssessmentState(
        input_type="url",
        input_value=test_page,
        findings=scan_result["findings"]
    )

    agg_result = aggregator_node(agg_state)

    assert "aggregated_findings" in agg_result
    aggregated = agg_result["aggregated_findings"]
    assert len(aggregated) > 0

    for finding in aggregated:
        assert finding.wcag_criterion != "unmapped", "expected a real WCAG mapping, not the fallback placeholder"
        assert finding.level in {"A", "AA", "AAA"}
        assert finding.severity in {"critical", "serious", "moderate", "minor"}
        assert finding.confidence in {"high", "needs_review"}


def test_aggregator_handles_zero_findings():
    """A clean page (zero findings) should short-circuit without calling the LLM."""
    state = AssessmentState(
        input_type="url", input_value="https://example.com", findings=[])
    result = aggregator_node(state)

    assert result == {"aggregated_findings": []}
