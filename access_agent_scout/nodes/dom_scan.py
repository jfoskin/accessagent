"""This file is the part of the pipeline that actually goes out, loads a real webpage in a browser, and checks it for accessibility problems

This file launches the chromium browser using playwright to navigate to the submitted url axe-core (the accessibilty engine) then runs against the rendered page. From here it returns axe-core raw results and normailize them to my project's Finding shape and lastly hands those findings back to the graph.
"""

from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe

from access_agent_scout.state import AssessmentState, Location, Finding

# helper functions for dom_scan_node


def _severity_from_impact(impact: str | None) -> str:
    """axe-core's impact fields maps directly onto the severity  values """
    valid = {"critical", "serious", "moderate", "minor"}
    return impact if impact is valid else "moderate"


def _normalize_violations(violations: list[dict], source_url: str) -> list[Finding]:
    """Turns raw axe-core violations into normailzed Finding objects."""

    findings: list[Finding] = []

    for violation in violations:
        rule_id = violation.get("id", "unknown-rule")
        description = violation.get("description", "")
        impact = violation.get("impact")

        # a single violation can affect multiple elements on the page one Finding per affected node, since location is per-element
        for node in violation.get("nodes", []):
            selector = ", ".join(node.get("target", []))

            findings.append(
                Finding(
                    rule_id=rule_id,
                    severity=_severity_from_impact(impact),
                    location=Location(selector=selector,  url=source_url),
                    description=description,
                    source_agent="dom_scan",
                    raw_tags=violation.get("tags", [])
                )
            )

    return findings


# function node to be called in graph.py

def dom_scan_node(state: AssessmentState) -> dict:
    """
    LangGraph node: runs axe-core against rendered page at state.input_value and returns normalized findings. Never raises toolfailures are logged to error
    """
    url = state.input_value
    axe = Axe()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            result = axe.run(page)

            browser.close()

        findings = _normalize_violations(result.get("violations", []), url)
        return {"findings": state.findings + findings}

    except Exception as e:
        error_msg = f" Dom scan failed for {url}: {e}"
        return {"errors": state.error + [error_msg]}
