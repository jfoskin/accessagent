from access_agent_scout.state import AggregatedFinding
from access_agent_scout.llm import get_llm
from pydantic import BaseModel


class Explanation(BaseModel):
    why_it_matters: str
    suggested_fix: str


def explain_finding(finding: AggregatedFinding) -> Explanation:
    llm = get_llm().with_structured_output(Explanation)

    prompt = f"""For this accessibility finding, explain why it matters in 
        plain language (1-2 sentences, no jargon) and suggest a concrete fix:

        Rule: {finding.rule_id}
        Description: {finding.description}
        Severity: {finding.severity}
        WCAG Criterion: {finding.wcag_criterion or "N/A (best practice)"}
        Affected element (CSS selector): {finding.location.selector or "not available"}

        Your suggested_fix must reference the actual selector/element shown above 
        where relevant — do not use generic placeholder examples like renaming 
        'button1' to 'button1'. If you can't give a concrete fix without seeing 
        the full page markup, say what to look for and check instead."""

    return llm.invoke(prompt)
