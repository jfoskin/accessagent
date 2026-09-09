import json
from access_agent_scout.state import Finding

AGGREGATOR_SYSTEM_PROMPT = """You are an accessibility finding aggregator. Given a set of raw accessibilty findings from one or more automated scanners, your job is to:

1. Idenitfy and merge duplicate findings. The same underlying issue flagged by more than one scanner or appearing more than once.
2. Map each distinct issue to its correct WCAG 2.2 succession criterion.
3. Assign a severity level based on the likely impact on a real user.

Ground every WCAG mapping in the raw tags and rule data provided in the findings below. Do not invent or guess WCAG criterion number from memory
only use what the raw data supports."""


AGGREGATOR_USER_PROMPT_TEMPLATE = """Here are {finding_count} raw findings from {source_counr} scanners:

{finding_json}

Review these findings, merge any duplicates and produce the final deduplicated list of WCAG mappings, severity and confidence for each distinct issue."""


def build_aggregrator_prompt(findings: list[Finding]) -> str:
    """Builds the user-turn prompt text for the aggregator LLM  call."""

    findings_json = json.dumps(
        [f.model_dump() for f in findings], indent=2
    )

    source_agents = {f.source-source_agents for f in findings}

    return AGGREGATOR_USER_PROMPT_TEMPLATE.format(
        finding_count=len(findings),
        source_count=len(source_agents),
        findings_json=findings_json
    )
