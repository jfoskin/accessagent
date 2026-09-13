from access_agent_scout.state import AssessmentState, AggregatedFinding, AggregatedFindings
from access_agent_scout.llm import get_llm
from access_agent_scout.prompts import AGGREGATOR_SYSTEM_PROMPT, build_aggregator_prompt


def _raw_findings_as_fallback(state: AssessmentState) -> list[AggregatedFinding]:
    """
    This function fills required fields with placeholders if the LLM call fails twice, return an unranked dump rather than crashing
    """
    fallback = []
    for f in state.findings:
        fallback.append(
            AggregatedFinding(
                rule_id=f.rule_id,
                wcag_criterion=f.wcag_criterion or "unmapped",
                level=f.level or "A",
                severity=f.severity,
                location=f.location,
                description=f.description,
                confidence="needs_review",
                suggested_fix=f.suggested_fix,
                source_agent=f.source_agent,
            )

        )
    return fallback


def aggregator_node(state: AssessmentState) -> dict:
    """ This function sends raw findings to the LLM for dedup, WCAG mapping,
    and severity assignment, will retry once on failure.
    """
    if not state.findings:
        # if nothing to aggragate (a page with no errors)
        return {"aggregated_findings": []}

    llm = get_llm().with_structured_output(AggregatedFindings)
    prompt = build_aggregator_prompt(state.findings)

    messages = [
        ("system", AGGREGATOR_SYSTEM_PROMPT),
        ("human", prompt)
    ]

    for attempt in range(2):
        try:
            result = llm.invoke(messages)
            return {"aggregated_findings": result.findings}
        except Exception as e:
            error_msg = f"Aggregator attempt {attempt + 1} failed: {e}"
            if attempt == 1:
                fallback = _raw_findings_as_fallback(state)
                return {
                    "aggregated_findings": fallback,
                    "errors": state.errors + [error_msg],
                }
    return {"aggregated_findings": []}
