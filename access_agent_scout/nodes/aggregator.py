
from access_agent_scout.state import AssessmentState, AggregatedFinding


def _dedupe_findings(findings: list) -> list[AggregatedFinding]:
    """
    Deterministic dedup for a single scanner source: the same rule_id
    affecting the same selector is the same underlying issue.

    This replaces LLM-based aggregation for Phase 1. Once a second
    scanner source exists (Phase 2+), cross-source dedup will need
    fuzzy/semantic matching — that's where an LLM earns its place;
    within one source, this is a mechanical, unambiguous match.
    """
    seen: dict[tuple[str, str | None], AggregatedFinding] = {}

    for f in findings:
        key = (f.rule_id, f.location.selector)
        if key not in seen:
            seen[key] = AggregatedFinding(
                rule_id=f.rule_id,
                wcag_criterion=f.wcag_criterion,
                level=f.level,
                is_best_practice=f.wcag_criterion is None,
                severity=f.severity,
                location=f.location,
                description=f.description,
                confidence="high",
                suggested_fix=f.suggested_fix,
                source_agent=f.source_agent,
            )

    return list(seen.values())


def aggregator_node(state: AssessmentState) -> dict:
    """
    Phase 1: deterministic dedup only, since a single scanner source has
    no real ambiguity to resolve — WCAG mapping already comes from
    axe-core's own tags, not the LLM. LLM-based aggregation returns in
    Phase 2+, when cross-source dedup requires real judgment.
    """
    if not state.findings:
        return {"aggregated_findings": []}

    aggregated = _dedupe_findings(state.findings)
    return {"aggregated_findings": aggregated}
