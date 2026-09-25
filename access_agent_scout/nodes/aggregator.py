from access_agent_scout.state import AssessmentState, AggregatedFinding, AggregatedFindings
from access_agent_scout.llm import get_llm
from access_agent_scout.prompts import AGGREGATOR_SYSTEM_PROMPT, build_aggregator_prompt
from access_agent_scout.wcag_reference


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


ddef aggregator_node(state: AssessmentState) -> dict:
    if not state.findings:
        return {"aggregated_findings": []}

    # keep a lookup from rule_id back to the original, axe-core-derived values
    original_by_rule = {f.rule_id: f for f in state.findings}

    llm = get_llm().with_structured_output(AggregatedFindings)
    prompt = build_aggregator_prompt(state.findings)
    messages = [("system", AGGREGATOR_SYSTEM_PROMPT), ("human", prompt)]

    attempt_errors = []
    for attempt in range(2):
        try:
            result = llm.invoke(messages)
            findings = result.findings

            # enforce ground truth regardless of what the LLM returned
            for finding in findings:
                original = original_by_rule.get(finding.rule_id)
                if original:
                    finding.wcag_criterion = original.wcag_criterion
                    finding.level = original.level
                    finding.is_best_practice = original.wcag_criterion is None

            return {"aggregated_findings": findings}
        except Exception as e:
            error_msg = f"Aggregator attempt {attempt + 1} failed: {e}"
            attempt_errors.append(error_msg)
            if attempt == 1:
                fallback = _raw_findings_as_fallback(state)
                return {"aggregated_findings": fallback, "errors": state.errors + attempt_errors}
