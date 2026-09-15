from access_agent_scout.state import AssessmentState
from access_agent_scout.graph import compiled_graph


def test_graph_runs_end_to_end():
    """Confirms the full graph runs without crashing against a real live URL."""
    state = AssessmentState(
        input_type="url", input_value="https://ghostingpen.net")

    # confirming the graph doesn't crash and that each piece of the pipeline is wired correectly
    result = compiled_graph.invoke(state)

    # confirms graph reaches the aggregator
    assert "aggregated_findings" in result
    assert isinstance(result["findings"], list)
    assert isinstance(result["aggregated_findings"], list)

    # aggregated_findings should be real AggregatedFinding objects now,
    # not a passthrough of raw findings
    for finding in result["aggregated_findings"]:
        assert finding.wcag_criterion is not None
        assert finding.level in {"A", "AA", "AAA"}
