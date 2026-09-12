from pathlib import Path

from access_agent_scout.state import AssessmentState
from access_agent_scout.nodes.dom_scan import dom_scan_node


def test_dom_scan_finds_known_violations():
    """Test to confirm dom scan is working correctly when given a url"""

    # return this path as a url
    test_page = (Path(__file__).parent / "fixtures" /
                 "test_page.html").resolve().as_uri()

    state = AssessmentState(input_type="url", input_value=test_page)
    result = dom_scan_node(state)

    # The following statement must be True if not an AssertionError is thrown
    # Checks that the dictionary dom_scan_node returned actually has a "findings" key in it, then pulls out the list of findings, then checks it's not empty.

    assert "findings" in result
    findings = result["findings"]
    assert len(
        findings) > 0, "expected at least one violation on the known-bad test page"

    # Loops through every finding and checks each one is shaped correctly
    for finding in findings:
        assert finding.rule_id
        assert finding.severity in {"critical", "serious", "moderate", "minor"}
        assert finding.location is not None
        assert finding.source_agent == "dom_scan"

    # checks if at least one finding in the list has a non-empty raw_tags list.
    assert any(finding.raw_tags for finding in findings), (
        "expected at least one finding to carry raw WCAG tags"
    )


def test_dom_scan_handles_bad_url():
    """ test if dom_scan handles the bad url gracefully"""

    state = AssessmentState(
        input_type="url", input_value="https://this-domain-does-not-exist-xyz123.invalid")
    result = dom_scan_node(state)

    assert "errors" in result
    assert len(result["errors"]) > 0
