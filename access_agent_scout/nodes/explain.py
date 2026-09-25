from access_agent_scout.state import AggregatedFinding
from access_agent_scout.llm import get_llm
from pydantic import BaseModel


class Explanation(BaseModel):
    why_it_matters: str
    suggested_fix: str


def explain_finding(finding: AggregatedFinding) -> Explanation:
    """Generates why_it_matters + suggested_fix for ONE finding, on demand.
    Called lazily from the UI, not upfront for every finding in a scan."""
    llm = get_llm().with_structured_output(Explanation)

    prompt = f"""For this accessibility finding, explain why it matters in \
    plain language (1-2 sentences, no jargon) and suggest a concrete fix:

    Rule: {finding.rule_id}
    Description: {finding.description}
    Severity: {finding.severity}
    WCAG Criterion: {finding.wcag_criterion or "N/A (best practice)"}"""

    return llm.invoke(prompt)
